# Frontend Integration Guide: Question Reply Draft Functionality

## Overview

The question reply system now supports **draft functionality**, allowing municipalities to save their answers as drafts before final submission. Draft replies are private and only visible to the author until they are published.

## Key Concepts

- **Draft (Private)**: Reply saved as draft - only visible to the author
- **Published (Public)**: Reply is finalized and visible to all users
- **Status**: Replies have a `reply_status` field with values `"private"` (draft) or `"public"` (published)

---

## API Changes

### 1. Answer Question Endpoint

**Endpoint**: `POST /api/v1/questions/{question_id}/answer`

**New Parameter**: `is_draft` (boolean, form field)

#### Request Format

```javascript
// Using FormData (multipart/form-data)
const formData = new FormData();
formData.append('reply_text', 'Your answer text here');
formData.append('is_draft', 'false'); // or 'true' for draft
formData.append('project_id', 'PROJECT-123');

// Optional: Add files
if (files && files.length > 0) {
  files.forEach(file => {
    formData.append('files', file);
  });
}

// Optional: Organization ID (auto-fetched if not provided and files are uploaded)
if (organizationId) {
  formData.append('organization_id', organizationId);
}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `reply_text` | string | ✅ Yes | Answer text provided by municipality |
| `is_draft` | boolean | ❌ No | Default: `false`. Set to `true` to save as draft, `false` to publish |
| `project_id` | string | ✅ Yes | Project reference ID (query parameter) |
| `files` | File[] | ❌ No | Optional file(s) to upload |
| `organization_id` | string | ❌ No | Organization ID (auto-fetched if not provided and files are uploaded) |

#### Response Structure

```json
{
  "status": "success",
  "message": "Question answered successfully",
  "data": {
    "id": 1,
    "project_id": "PROJECT-123",
    "asked_by": "lender_user_id",
    "question_text": "What is the project timeline?",
    "status": "answered", // or "open" if draft
    "answer": {
      "id": 1,
      "question_id": 1,
      "replied_by_user_id": "municipality_user_id",
      "reply_text": "The project will be completed in 6 months.",
      "reply_status": "public", // or "private" for draft
      "documents": [
        {
          "id": 1,
          "file_id": 123,
          "file": {
            "id": 123,
            "file_name": "document.pdf",
            "file_path": "...",
            // ... other file metadata
          }
        }
      ],
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  }
}
```

---

### 2. Update Answer Endpoint

**Endpoint**: `PUT /api/v1/questions/{question_id}/answer`

**New Parameter**: `is_draft` (boolean, form field)

#### Request Format

```javascript
const formData = new FormData();
formData.append('reply_text', 'Updated answer text');
formData.append('is_draft', 'false'); // Change draft to published, or vice versa
formData.append('project_id', 'PROJECT-123');

// Optional: Replace existing files
if (newFiles && newFiles.length > 0) {
  newFiles.forEach(file => {
    formData.append('files', file);
  });
}
```

#### Parameters

Same as Answer Question endpoint, with the addition that:
- If `files` is provided, existing documents are **replaced** with new ones
- If `files` is not provided, existing documents remain unchanged
- If `files` is an empty array, all existing documents are removed

#### Response Structure

Same as Answer Question endpoint.

---

### 3. List Questions Endpoint

**Endpoint**: `GET /api/v1/questions/`

**Behavior Change**: Private (draft) replies are automatically filtered out unless the current user is the author.

#### Request Format

```javascript
// No changes needed - existing request format works
const params = new URLSearchParams({
  project_id: 'PROJECT-123',
  // or
  organization_id: 'ORG-456',
  status_filter: 'answered', // optional
  category: 'financial', // optional
  priority: 'high', // optional
  skip: 0,
  limit: 50
});

fetch(`/api/v1/questions/?${params}`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

#### Response Behavior

- **Public replies**: Visible to all users
- **Private (draft) replies**: Only visible to the author
- If a question has a private reply, the `answer` field will be `null` for other users

---

### 4. Get Question Endpoint

**Endpoint**: `GET /api/v1/questions/{question_id}`

**Behavior Change**: Private (draft) replies are automatically filtered out unless the current user is the author.

#### Request Format

```javascript
// No changes needed - existing request format works
fetch(`/api/v1/questions/${questionId}?project_id=${projectId}`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

#### Response Behavior

- If the reply is private and the user is not the author, `answer` will be `null`
- If the reply is private and the user is the author, `answer` will be included with `reply_status: "private"`

---

## Frontend Implementation Guide

### 1. Save as Draft Button

```javascript
// Example: React component
const handleSaveDraft = async () => {
  const formData = new FormData();
  formData.append('reply_text', answerText);
  formData.append('is_draft', 'true'); // ✅ Save as draft
  formData.append('project_id', projectId);

  if (selectedFiles.length > 0) {
    selectedFiles.forEach(file => {
      formData.append('files', file);
    });
  }

  try {
    const response = await fetch(`/api/v1/questions/${questionId}/answer?project_id=${projectId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });

    const data = await response.json();
    if (data.status === 'success') {
      // Show success message
      alert('Draft saved successfully!');
      // Update UI to show draft status
      setDraftStatus('private');
    }
  } catch (error) {
    console.error('Error saving draft:', error);
  }
};
```

### 2. Submit Final Answer Button

```javascript
const handleSubmitAnswer = async () => {
  const formData = new FormData();
  formData.append('reply_text', answerText);
  formData.append('is_draft', 'false'); // ✅ Publish (final submit)
  formData.append('project_id', projectId);

  if (selectedFiles.length > 0) {
    selectedFiles.forEach(file => {
      formData.append('files', file);
    });
  }

  try {
    const response = await fetch(`/api/v1/questions/${questionId}/answer?project_id=${projectId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });

    const data = await response.json();
    if (data.status === 'success') {
      // Show success message
      alert('Answer submitted successfully!');
      // Update UI - question status will be "answered"
      setDraftStatus('public');
    }
  } catch (error) {
    console.error('Error submitting answer:', error);
  }
};
```

### 3. Update Existing Draft/Answer

```javascript
const handleUpdateAnswer = async (isDraft) => {
  const formData = new FormData();
  formData.append('reply_text', updatedAnswerText);
  formData.append('is_draft', isDraft ? 'true' : 'false');
  formData.append('project_id', projectId);

  // Optional: Replace files
  if (newFiles.length > 0) {
    newFiles.forEach(file => {
      formData.append('files', file);
    });
  }

  try {
    const response = await fetch(`/api/v1/questions/${questionId}/answer?project_id=${projectId}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });

    const data = await response.json();
    if (data.status === 'success') {
      alert(isDraft ? 'Draft updated!' : 'Answer updated and published!');
    }
  } catch (error) {
    console.error('Error updating answer:', error);
  }
};
```

### 4. Display Draft Status in UI

```javascript
// Example: Show draft badge
const AnswerDisplay = ({ answer }) => {
  if (!answer) return null;

  return (
    <div className="answer-container">
      {answer.reply_status === 'private' && (
        <span className="draft-badge">Draft</span>
      )}
      <p>{answer.reply_text}</p>
      {answer.documents && answer.documents.length > 0 && (
        <div className="documents">
          {answer.documents.map(doc => (
            <a key={doc.id} href={doc.file.file_path}>
              {doc.file.file_name}
            </a>
          ))}
        </div>
      )}
    </div>
  );
};
```

### 5. Handle Draft Visibility

```javascript
// When listing questions, check if answer exists and is visible
const QuestionList = ({ questions }) => {
  return questions.map(question => (
    <div key={question.id}>
      <h3>{question.question_text}</h3>
      <p>Status: {question.status}</p>
      
      {question.answer ? (
        <div>
          {question.answer.reply_status === 'private' && (
            <span className="draft-indicator">[Draft - Only you can see this]</span>
          )}
          <p>{question.answer.reply_text}</p>
        </div>
      ) : (
        <p>No answer yet</p>
      )}
    </div>
  ));
};
```

---

## UI/UX Recommendations

### 1. Draft Indicator

- Show a clear "Draft" badge or indicator when `reply_status === "private"`
- Use a different color scheme (e.g., yellow/orange) for draft replies
- Add tooltip: "This is a draft. Only you can see it."

### 2. Button States

- **Save Draft**: Always enabled, saves as `is_draft: true`
- **Submit Answer**: Enabled when ready, saves as `is_draft: false`
- **Update Draft**: If draft exists, show "Update Draft" and "Publish" buttons

### 3. Question Status Display

- If question has a **public** reply → Status: "answered" (green)
- If question has a **private** reply → Status: "open" (but show draft indicator)
- If question has no reply → Status: "open"

### 4. Workflow Example

```
1. User types answer → Shows "Save Draft" and "Submit Answer" buttons
2. User clicks "Save Draft" → Answer saved as private, question status remains "open"
3. User can edit and click "Save Draft" again → Updates existing draft
4. User clicks "Submit Answer" → Answer published as public, question status becomes "answered"
5. After publishing, user can still update → Shows "Update Answer" button
```

---

## Error Handling

### Common Scenarios

1. **Draft Already Exists**
   - If a draft exists and user tries to create a new answer, the API will automatically update the existing draft
   - No error - this is expected behavior

2. **Publishing Draft**
   - When changing `is_draft` from `true` to `false`, the question status automatically changes to "answered"
   - No additional API call needed

3. **Viewing Private Replies**
   - If user is not the author, `answer` field will be `null` in the response
   - Handle this gracefully in UI (show "No answer yet" or "Answer pending")

---

## Testing Checklist

- [ ] Save answer as draft (`is_draft: true`)
- [ ] Verify draft is only visible to author
- [ ] Verify draft is hidden from other users
- [ ] Submit answer as final (`is_draft: false`)
- [ ] Verify published answer is visible to all users
- [ ] Update existing draft
- [ ] Change draft to published
- [ ] Change published to draft (if needed)
- [ ] Upload files with draft
- [ ] Upload files with published answer
- [ ] Replace files in existing answer

---

## Migration Notes

### Backward Compatibility

- The `is_draft` parameter is **optional** and defaults to `false` (published)
- Existing API calls without `is_draft` will continue to work
- All existing replies in the database will be treated as "public" (you may need to set default in migration)

### Response Changes

- All answer responses now include `reply_status` field
- Question status remains "open" if reply is a draft
- Question status becomes "answered" only when reply is published

---

## Example: Complete React Component

```jsx
import React, { useState } from 'react';

const QuestionAnswerForm = ({ questionId, projectId, token }) => {
  const [answerText, setAnswerText] = useState('');
  const [files, setFiles] = useState([]);
  const [isDraft, setIsDraft] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (saveAsDraft) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('reply_text', answerText);
    formData.append('is_draft', saveAsDraft ? 'true' : 'false');
    formData.append('project_id', projectId);

    files.forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await fetch(
        `/api/v1/questions/${questionId}/answer?project_id=${projectId}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        }
      );

      const data = await response.json();
      
      if (data.status === 'success') {
        alert(saveAsDraft ? 'Draft saved!' : 'Answer submitted!');
        // Reset form or navigate
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to save answer');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="answer-form">
      <textarea
        value={answerText}
        onChange={(e) => setAnswerText(e.target.value)}
        placeholder="Enter your answer..."
      />
      
      <input
        type="file"
        multiple
        onChange={(e) => setFiles(Array.from(e.target.files))}
      />

      <div className="button-group">
        <button
          onClick={() => handleSubmit(true)}
          disabled={loading || !answerText}
        >
          Save Draft
        </button>
        <button
          onClick={() => handleSubmit(false)}
          disabled={loading || !answerText}
          className="primary"
        >
          Submit Answer
        </button>
      </div>
    </div>
  );
};

export default QuestionAnswerForm;
```

---

## Support

For questions or issues, please contact the backend team or refer to the API documentation.

**Last Updated**: 2024-01-15
