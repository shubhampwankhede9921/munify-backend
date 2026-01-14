from typing import Optional, Tuple, List, Union

from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session, joinedload

from app.core.logging import get_logger
from app.models.project import Project
from app.models.question import Question, QuestionReply
from app.models.question_reply_document import QuestionReplyDocument
from app.services.file_service import FileService
from app.schemas.question import (
    QuestionCreate,
    QuestionUpdate,
)

logger = get_logger("services.question")


class QuestionService:
    def __init__(self, db: Session):
        self.db = db

    def _validate_project_exists(self, project_id: str) -> Project:
        """Validate that project exists for the given project_reference_id."""
        project = (
            self.db.query(Project)
            .filter(Project.project_reference_id == project_id)
            .first()
        )
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with reference ID '{project_id}' not found",
            )
        return project

    def _validate_question_status_for_answer(self, question: Question) -> None:
        """Ensure question is in a state that can be answered."""
        if question.status in ("closed",):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot answer a question in '{question.status}' status",
            )

    def create_question(self, data: QuestionCreate, username: Optional[str] = None) -> Question:
        """Create a new question for a project."""
        logger.info(
            "Creating question for project %s by %s",
            data.project_id,
            username or data.asked_by,
        )

        try:
            # Validate project exists
            self._validate_project_exists(data.project_id)

            question_dict = data.model_dump(exclude_unset=True)
            # Use username from auth context if provided, otherwise fall back to asked_by from request
            if username:
                question_dict["asked_by"] = username
                question_dict["created_by"] = username
            # Ensure default values consistent with DB defaults
            if "status" not in question_dict or question_dict["status"] is None:
                question_dict["status"] = "open"
            if "is_public" not in question_dict or question_dict["is_public"] is None:
                question_dict["is_public"] = True
            if "priority" not in question_dict or question_dict["priority"] is None:
                question_dict["priority"] = "normal"

            question = Question(**question_dict)
            self.db.add(question)
            self.db.commit()
            self.db.refresh(question)

            logger.info("Question %s created successfully", question.id)
            return question
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as exc:
            self.db.rollback()
            logger.error("Error creating question: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create question: {str(exc)}",
            )

    def list_questions(
        self,
        project_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        status_filter: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
        current_username: Optional[str] = None,
    ) -> Tuple[List[Question], int]:
        """List questions with optional filters and pagination.
        
        Can filter by project_id (project_reference_id) and/or organization_id.
        If project_id is provided, validates that the project exists.
        Private replies are filtered out unless current_username is the author.
        
        Args:
            current_username: Current user's username to check if they can view private replies
        """
        # Validate project exists if project_id is provided
        if project_id:
            self._validate_project_exists(project_id)

        # Start building query with join to Project if organization_id filter is needed
        if organization_id:
            query = (
                self.db.query(Question)
                .join(Project, Question.project_id == Project.project_reference_id)
                .options(
                    joinedload(Question.answer).joinedload(QuestionReply.documents).joinedload(QuestionReplyDocument.file)
                )
                .filter(Project.organization_id == organization_id)
            )
        else:
            query = (
                self.db.query(Question)
                .options(
                    joinedload(Question.answer).joinedload(QuestionReply.documents).joinedload(QuestionReplyDocument.file)
                )
            )

        # Apply project_id filter if provided
        if project_id:
            query = query.filter(Question.project_id == project_id)

        # Apply other filters
        if status_filter:
            query = query.filter(Question.status == status_filter)
        if category:
            query = query.filter(Question.category == category)
        if priority:
            query = query.filter(Question.priority == priority)

        total = query.count()

        questions = (
            query.order_by(Question.created_at.desc(), Question.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        # Filter: Only show public replies, OR private replies if user is the author
        # This ensures only "public" status replies are visible to other users
        for question in questions:
            if question.answer:
                # Only show public replies to all users
                # OR show private replies only if current_username is the author
                if question.answer.reply_status == "private":
                    # Private reply: only visible to author
                    reply_author = question.answer.replied_by_user_id
                    if not current_username or reply_author != current_username:
                        # Hide private reply from non-authors - only public replies should be visible
                        logger.debug(
                            "Filtering out private reply for question %s (author: %s, viewer: %s)",
                            question.id,
                            reply_author,
                            current_username
                        )
                        question.answer = None
                # If reply_status is "public", it's visible to everyone (no filtering needed)

        return questions, total

    def get_question(self, project_id: str, question_id: int, current_username: Optional[str] = None) -> Question:
        """
        Get a single question for a project, including its answer and documents.
        
        Args:
            project_id: Project reference ID
            question_id: Question ID
            current_username: Current user's username to check if they can view private replies
        """
        self._validate_project_exists(project_id)

        question = (
            self.db.query(Question)
            .options(
                joinedload(Question.answer).joinedload(QuestionReply.documents).joinedload(QuestionReplyDocument.file)
            )
            .filter(Question.id == question_id, Question.project_id == project_id)
            .first()
        )
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question with ID {question_id} not found for project '{project_id}'",
            )
        
        # Filter out private replies unless user is the author
        if question.answer and question.answer.reply_status == "private":
            if not current_username or question.answer.replied_by_user_id != current_username:
                # Remove private answer from response
                question.answer = None
        
        return question

    def update_question(
        self,
        project_id: str,
        question_id: int,
        data: QuestionUpdate,
        user_id: Optional[str] = None,  # Actually stores username now
    ) -> Question:
        """Update question fields (e.g., text, category, priority, status).

        If the question already has an answer, modification is not allowed.
        """
        question = self.get_question(project_id, question_id)

        if question.answer:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot modify question because it already has an answer",
            )

        update_dict = data.model_dump(exclude_unset=True)
        # Set updated_by from auth context if provided (stores username)
        if user_id:
            question.updated_by = user_id
        
        for field, value in update_dict.items():
            setattr(question, field, value)

        try:
            self.db.commit()
            self.db.refresh(question)
            return question
        except Exception as exc:
            self.db.rollback()
            logger.error("Error updating question %s: %s", question_id, str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update question: {str(exc)}",
            )

    def _delete_existing_documents(
        self,
        question_reply_id: int,
        deleted_by: str,
    ) -> None:
        """
        Delete all existing documents for a question reply.
        
        This includes:
        1. Deleting QuestionReplyDocument records
        2. Soft deleting associated files from perdix_mp_files
        """
        existing_documents = (
            self.db.query(QuestionReplyDocument)
            .filter(QuestionReplyDocument.question_reply_id == question_reply_id)
            .all()
        )
        
        if not existing_documents:
            return
        
        file_service = FileService(self.db)
        
        for doc in existing_documents:
            try:
                file_service.delete_file(doc.file_id, deleted_by)
                self.db.delete(doc)
                logger.info(
                    "Deleted existing document: document_id=%s, file_id=%s",
                    doc.id,
                    doc.file_id,
                )
            except Exception as exc:
                logger.error(
                    "Failed to delete existing document %s: %s", doc.id, str(exc)
                )
        
        self.db.commit()

    def _upload_and_link_answer_documents(
        self,
        question_reply_id: int,
        files: Optional[Union[UploadFile, List[UploadFile]]],
        organization_id: str,
        project_reference_id: str,
        uploaded_by: str,
    ) -> None:
        """
        Upload files and link them to a question reply.
        
        Args:
            question_reply_id: ID of the question reply
            files: Single file or list of files to upload
            organization_id: Organization ID
            project_reference_id: Project reference ID
            uploaded_by: User ID who uploaded the files
        """
        if not files:
            return
        
        # Normalize to list if single file
        # Direct check: if it's a list or tuple, use it; otherwise wrap in list
        if isinstance(files, list):
            files_list = files
        elif isinstance(files, tuple):
            files_list = list(files)
        else:
            # Single file or other type - wrap in list
            files_list = [files]
        
        logger.debug(f"Processing {len(files_list)} file(s) for question_reply_id={question_reply_id}, type={type(files)}")
        
        file_service = FileService(self.db)
        uploaded_files = []
        
        try:
            for file in files_list:
                # Upload file
                perdix_file = file_service.upload_file(
                    file=file,
                    organization_id=organization_id,
                    uploaded_by=uploaded_by,
                    file_category="Additional",
                    document_type="QandA",
                    access_level="private",
                    project_reference_id=project_reference_id,
                    question_reply_id=question_reply_id,
                    created_by=uploaded_by,
                )
                uploaded_files.append(perdix_file)
                
                # Create mapping record
                question_reply_doc = QuestionReplyDocument(
                    question_reply_id=question_reply_id,
                    file_id=perdix_file.id,
                    uploaded_by=uploaded_by,
                    created_by=uploaded_by,
                )
                self.db.add(question_reply_doc)
            
            self.db.commit()
            logger.info(
                "Uploaded and linked %d documents for question_reply_id=%s",
                len(uploaded_files),
                question_reply_id,
            )
        except Exception as exc:
            self.db.rollback()
            # Rollback: Delete uploaded files if mapping creation fails
            for perdix_file in uploaded_files:
                try:
                    file_service.delete_file(perdix_file.id, uploaded_by)
                except Exception as delete_exc:
                    logger.error(
                        "Failed to rollback file %s: %s", perdix_file.id, str(delete_exc)
                    )
            logger.error(
                "Error uploading documents for question_reply_id %s: %s",
                question_reply_id,
                str(exc),
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload documents: {str(exc)}",
            )

    def answer_question(
        self,
        project_id: str,
        question_id: int,
        replied_by_username: str,
        reply_text: str,
        organization_id: Optional[str] = None,
        files: Optional[List[UploadFile]] = None,
        is_draft: bool = False,
    ) -> Question:
        """
        Create an answer for a question.

        Enforces one answer per question; if an answer already exists, returns 409.
        
        Args:
            project_id: Project reference ID
            question_id: Question ID
            replied_by_username: Username of the user providing the answer
            reply_text: Answer text
            organization_id: Organization ID (auto-fetched from project if not provided and files are uploaded)
            files: Optional list of files to upload
            is_draft: If True, saves as draft (private), if False, publishes (public)
        """
        question = self.get_question(project_id, question_id)
        self._validate_question_status_for_answer(question)

        # Check if answer exists - allow update if it's a draft by the same user
        if question.answer:
            if question.answer.reply_status == "private" and question.answer.replied_by_user_id == replied_by_username:
                # Allow updating existing draft
                return self.update_answer(
                    project_id=project_id,
                    question_id=question_id,
                    replied_by_username=replied_by_username,
                    reply_text=reply_text,
                    organization_id=organization_id,
                    files=files,
                    is_draft=is_draft,
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Question already has an answer",
                )
        
        # Fetch organization_id from project if not provided and files are being uploaded
        if files and not organization_id:
            project = self._validate_project_exists(project_id)
            organization_id = project.organization_id
            logger.info(
                "Auto-fetched organization_id=%s from project %s for file upload",
                organization_id,
                project_id,
            )

        try:
            # Determine reply status based on is_draft
            reply_status = "private" if is_draft else "public"
            
            # Create answer first to get the ID
            answer = QuestionReply(
                question_id=question.id,
                replied_by_user_id=replied_by_username,  # Store username
                reply_text=reply_text,
                reply_status=reply_status,
                created_by=replied_by_username,  # Store username
            )
            self.db.add(answer)
            self.db.flush()  # Get the ID without committing
            
            # Upload and link documents if provided
            if files and organization_id:
                self._upload_and_link_answer_documents(
                    question_reply_id=answer.id,
                    files=files,
                    organization_id=organization_id,
                    project_reference_id=project_id,
                    uploaded_by=replied_by_username,  # Store username
                )

            # Update question status to answered only if reply is public
            if reply_status == "public":
                question.status = "answered"

            self.db.commit()
            self.db.refresh(question)
            # Reload with documents
            question = self.get_question(project_id, question_id, current_username=replied_by_username)
            return question
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as exc:
            self.db.rollback()
            logger.error(
                "Error creating answer for question %s: %s", question_id, str(exc)
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to answer question: {str(exc)}",
            )

    def update_answer(
        self,
        project_id: str,
        question_id: int,
        replied_by_username: str,
        reply_text: str,
        organization_id: Optional[str] = None,
        files: Optional[List[UploadFile]] = None,
        is_draft: bool = False,
    ) -> Question:
        """
        Update existing answer for a question.
        
        If files are provided, existing documents are replaced with new ones.
        
        Args:
            project_id: Project reference ID
            question_id: Question ID
            replied_by_username: Username of the user updating the answer
            reply_text: Updated answer text
            organization_id: Organization ID (auto-fetched from project if not provided and files are uploaded)
            files: Optional list of files to upload (replaces existing documents)
            is_draft: If True, saves as draft (private), if False, publishes (public)
        """
        question = self.get_question(project_id, question_id, current_username=replied_by_username)
        if not question.answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found for this question",
            )

        answer = question.answer

        # Optionally, enforce that only the same user can update
        if replied_by_username != answer.replied_by_user_id:
            logger.warning(
                "User %s attempted to update answer %s owned by %s",
                replied_by_username,
                answer.id,
                answer.replied_by_user_id,
            )
        
        # Fetch organization_id from project if not provided and files are being uploaded
        if files and not organization_id:
            project = self._validate_project_exists(project_id)
            organization_id = project.organization_id
            logger.info(
                "Auto-fetched organization_id=%s from project %s for file upload",
                organization_id,
                project_id,
            )

        try:
            # Determine new reply status
            new_reply_status = "private" if is_draft else "public"
            old_reply_status = answer.reply_status
            
            # Update reply text and status
            answer.reply_text = reply_text
            answer.reply_status = new_reply_status
            answer.updated_by = replied_by_username  # Store username
            
            # If files are provided, replace existing documents
            if files is not None:
                # Delete existing documents
                self._delete_existing_documents(
                    question_reply_id=answer.id,
                    deleted_by=replied_by_username,  # Store username
                )
                
                # Upload and link new documents
                if files and organization_id:
                    self._upload_and_link_answer_documents(
                        question_reply_id=answer.id,
                        files=files,
                        organization_id=organization_id,
                        project_reference_id=project_id,
                        uploaded_by=replied_by_username,  # Store username
                    )

            # Update question status based on reply status change
            if old_reply_status == "private" and new_reply_status == "public":
                # Draft was published - mark question as answered
                question.status = "answered"
            elif old_reply_status == "public" and new_reply_status == "private":
                # Published answer was changed back to draft - keep question status as is
                # (don't change it back to "open" as it was already answered)
                pass

            self.db.commit()
            # Reload with documents
            question = self.get_question(project_id, question_id, current_username=replied_by_username)
            return question
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as exc:
            self.db.rollback()
            logger.error(
                "Error updating answer for question %s: %s", question_id, str(exc)
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update answer: {str(exc)}",
            )

    def delete_question(
        self,
        project_id: str,
        question_id: int,
        requested_by: str,
    ) -> None:
        """
        Delete a question written by the same person.

        If the question has an answer, deletion is not allowed
        (caller must delete the answer first).
        """
        question = self.get_question(project_id, question_id)

        # Only the author of the question can delete it
        if question.asked_by != requested_by:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the user who asked the question can delete it",
            )

        # If answer exists, do not allow deletion until answer is removed
        if question.answer:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete question because it already has an answer. Delete the answer first.",
            )

        try:
            self.db.delete(question)
            self.db.commit()
            logger.info(
                "Question %s for project %s deleted by %s",
                question_id,
                project_id,
                requested_by,
            )
        except Exception as exc:
            self.db.rollback()
            logger.error(
                "Error deleting question %s for project %s: %s",
                question_id,
                project_id,
                str(exc),
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete question: {str(exc)}",
            )

    def delete_answer(
        self,
        project_id: str,
        question_id: int,
        replied_by_username: str,
    ) -> Question:
        """
        Delete the answer for a question.

        After deletion, the question status is set back to 'open'.
        """
        question = self.get_question(project_id, question_id)

        if not question.answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found for this question",
            )

        answer = question.answer

        # Optionally enforce that only the same user can delete their answer
        if replied_by_username != answer.replied_by_user_id:
            logger.warning(
                "User %s attempted to delete answer %s owned by %s",
                replied_by_username,
                answer.id,
                answer.replied_by_user_id,
            )

        try:
            self.db.delete(answer)
            # Reset question status back to open
            question.status = "open"

            self.db.commit()
            self.db.refresh(question)
            return question
        except Exception as exc:
            self.db.rollback()
            logger.error(
                "Error deleting answer for question %s: %s",
                question_id,
                str(exc),
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete answer: {str(exc)}",
            )


