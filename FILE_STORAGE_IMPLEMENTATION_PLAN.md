# File Storage System Implementation Plan

## 📋 Table of Contents
1. [Overview](#overview)
2. [Architecture Design](#architecture-design)
3. [Component Breakdown](#component-breakdown)
4. [Implementation Strategy](#implementation-strategy)
5. [File Structure](#file-structure)
6. [API Design](#api-design)
7. [Security Considerations](#security-considerations)
8. [Best Practices](#best-practices)
9. [Step-by-Step Implementation](#step-by-step-implementation)
10. [Testing Strategy](#testing-strategy)

---

## 🎯 Overview

### Objective
Implement a generic, scalable file storage system using Amazon S3 that supports:
- **Upload**: Any file type (images, PDFs, videos, documents, etc.)
- **Download**: Secure file retrieval with access control
- **Metadata Management**: Track file information in database
- **Flexibility**: Support multiple file types and use cases

### Key Requirements
- ✅ Generic upload/download functions
- ✅ S3 integration with configuration in `.env`
- ✅ Database tracking via `perdix_mp_files` table
- ✅ Support for all file types (jpg, pdf, videos, etc.)
- ✅ Access level control (public, restricted, private)
- ✅ File validation and security
- ✅ Checksum verification (SHA-256)
- ✅ Download tracking
- ✅ **Hierarchical S3 folder structure** based on organization, category, and document type

---

## 🏗️ Architecture Design

### Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer                           │
│  (app/api/v1/endpoints/files.py)                      │
│  - HTTP request handling                               │
│  - Request validation                                  │
│  - Response formatting                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  Service Layer                          │
│  (app/services/file_service.py)                        │
│  - Business logic                                       │
│  - Database operations                                 │
│  - Access control validation                           │
│  - File metadata management                            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Storage Abstraction Layer                  │
│  (app/services/storage.py)                             │
│  - S3StorageService (primary)                          │
│  - LocalStorageService (fallback/dev)                  │
│  - Interface: upload_file(), download_file(),           │
│    delete_file(), generate_presigned_url()             │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              External Services                          │
│  - Amazon S3 (production)                              │
│  - Local Filesystem (development)                      │
│  - PostgreSQL (metadata)                               │
└─────────────────────────────────────────────────────────┘
```

### Design Patterns Used
1. **Strategy Pattern**: Storage service abstraction (S3 vs Local)
2. **Repository Pattern**: Database operations in service layer
3. **Dependency Injection**: Services receive DB session
4. **Factory Pattern**: Storage service factory based on config
5. **Builder Pattern**: Path builder for hierarchical folder structure
6. **Enum Pattern**: Type-safe folder and document type definitions

---

## 🔧 Component Breakdown

### 1. Configuration (`app/core/config.py`)
**Purpose**: Centralized S3 configuration management

**Environment Variables**:
```env
# S3 Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
AWS_S3_BUCKET_NAME=your-bucket-name
AWS_S3_ENDPOINT_URL=  # Optional: for S3-compatible services (MinIO, etc.)
STORAGE_TYPE=s3  # s3 or local (for development)

# File Upload Settings
MAX_FILE_SIZE_MB=100  # Maximum file size in MB
ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf,doc,docx,xls,xlsx,mp4,avi,mov,zip
UPLOAD_PATH_PREFIX=uploads  # S3 path prefix
```

### 2. Path Builder (`app/utils/path_builder.py`) ⭐ NEW
**Purpose**: Generate hierarchical S3 paths based on file context

**S3 Folder Structure**:
```
{org_id}/
├── KYC/
│   ├── PAN/
│   └── GST/
├── Project/
│   └── {project_reference_id}/
│       ├── DPR/
│       ├── Project Image/
│       └── Project videos/
└── Additional/
    └── {project_reference_id}/
        ├── commitment/
        └── Requested document/
```

**Key Components**:
- `FileCategory` enum: KYC, Project, Additional
- `KYCDocumentType` enum: PAN, GST
- `ProjectDocumentType` enum: DPR, Project Image, Project videos
- `AdditionalDocumentType` enum: commitment, Requested document
- `PathBuilder` class: Builds paths dynamically

**Example Usage**:
```python
# KYC Document
path = PathBuilder.build_kyc_path(
    org_id="org-123",
    document_type=KYCDocumentType.PAN,
    filename="pan_card.pdf"
)
# Returns: "org-123/KYC/PAN/pan_card.pdf"

# Project Document
path = PathBuilder.build_project_path(
    org_id="org-123",
    project_reference_id="PROJ-2024-00001",
    document_type=ProjectDocumentType.DPR,
    filename="dpr_document.pdf"
)
# Returns: "org-123/Project/PROJ-2024-00001/DPR/dpr_document.pdf"

# Additional Document
path = PathBuilder.build_additional_path(
    org_id="org-123",
    project_reference_id="PROJ-2024-00001",
    document_type=AdditionalDocumentType.COMMITMENT,
    filename="commitment_letter.pdf"
)
# Returns: "org-123/Additional/PROJ-2024-00001/commitment/commitment_letter.pdf"
```

### 3. Storage Service (`app/services/storage.py`)
**Purpose**: Abstract storage operations

**Interface Methods**:
```python
class StorageServiceInterface:
    def upload_file(
        file_bytes: bytes,
        filename: str,
        organization_id: str,
        content_type: str
    ) -> Tuple[str, str]:  # Returns (storage_path, checksum)
    
    def download_file(storage_path: str) -> bytes:
    
    def delete_file(storage_path: str) -> bool:
    
    def generate_presigned_url(
        storage_path: str,
        expiration: int = 3600
    ) -> str:  # For direct S3 access
    
    def file_exists(storage_path: str) -> bool:
```

**Implementation Classes**:
- `S3StorageService`: Production S3 implementation
- `LocalStorageService`: Development/fallback implementation

### 2.1 Path Builder System (`app/utils/path_builder.py`) ⭐ NEW
**Purpose**: Generate hierarchical S3 paths based on file context and document type

**S3 Folder Structure**:
```
{org_id}/
├── KYC/
│   ├── PAN/
│   └── GST/
├── Project/
│   └── {project_reference_id}/
│       ├── DPR/
│       ├── Project Image/
│       └── Project videos/
└── Additional/
    └── {project_reference_id}/
        ├── commitment/
        └── Requested document/
```

**Design Approach**:
- **Enum-based**: Type-safe folder and document type definitions
- **Builder Pattern**: Flexible path construction
- **Context-aware**: Paths generated based on file category and context
- **Extensible**: Easy to add new document types or categories

**Implementation Structure**:
```python
# Enums for type safety
class FileCategory(str, Enum):
    KYC = "KYC"
    PROJECT = "Project"
    ADDITIONAL = "Additional"

class KYCDocumentType(str, Enum):
    PAN = "PAN"
    GST = "GST"

class ProjectDocumentType(str, Enum):
    DPR = "DPR"
    PROJECT_IMAGE = "Project Image"
    PROJECT_VIDEOS = "Project videos"

class AdditionalDocumentType(str, Enum):
    COMMITMENT = "commitment"
    REQUESTED_DOCUMENT = "Requested document"

# Path Builder Class
class PathBuilder:
    @staticmethod
    def build_kyc_path(
        org_id: str,
        document_type: KYCDocumentType,
        filename: str
    ) -> str:
        """Build path for KYC documents: {org_id}/KYC/{document_type}/{filename}"""
        return f"{org_id}/KYC/{document_type.value}/{filename}"
    
    @staticmethod
    def build_project_path(
        org_id: str,
        project_reference_id: str,
        document_type: ProjectDocumentType,
        filename: str
    ) -> str:
        """Build path for project documents"""
        return f"{org_id}/Project/{project_reference_id}/{document_type.value}/{filename}"
    
    @staticmethod
    def build_additional_path(
        org_id: str,
        project_reference_id: str,
        document_type: AdditionalDocumentType,
        filename: str
    ) -> str:
        """Build path for additional documents"""
        return f"{org_id}/Additional/{project_reference_id}/{document_type.value}/{filename}"
```

**Usage Examples**:
```python
# KYC Document - PAN
path = PathBuilder.build_kyc_path(
    org_id="org-123",
    document_type=KYCDocumentType.PAN,
    filename="pan_card_abc123.pdf"
)
# Result: "org-123/KYC/PAN/pan_card_abc123.pdf"

# Project Document - DPR
path = PathBuilder.build_project_path(
    org_id="org-123",
    project_reference_id="PROJ-2024-00001",
    document_type=ProjectDocumentType.DPR,
    filename="dpr_document_v1.pdf"
)
# Result: "org-123/Project/PROJ-2024-00001/DPR/dpr_document_v1.pdf"

# Additional Document - Commitment
path = PathBuilder.build_additional_path(
    org_id="org-123",
    project_reference_id="PROJ-2024-00001",
    document_type=AdditionalDocumentType.COMMITMENT,
    filename="commitment_letter.pdf"
)
# Result: "org-123/Additional/PROJ-2024-00001/commitment/commitment_letter.pdf"
```

**Benefits**:
- ✅ **Type Safety**: Enums prevent typos and invalid values
- ✅ **Consistency**: Standardized folder structure across all uploads
- ✅ **Maintainability**: Single place to update folder structure
- ✅ **Extensibility**: Easy to add new categories or document types
- ✅ **Organization**: Files automatically organized by context
- ✅ **Scalability**: Structure supports millions of files

### 3. File Service (`app/services/file_service.py`)
**Purpose**: Business logic for file operations

**Key Methods**:
```python
class FileService:
    def upload_file(
        file: UploadFile,
        organization_id: str,
        uploaded_by: str,
        access_level: str = 'private',
        created_by: str = None
    ) -> PerdixFile
    
    def download_file(
        file_id: int,
        user_id: str,
        organization_id: str = None
    ) -> Tuple[bytes, PerdixFile]
    
    def get_file_metadata(file_id: int) -> PerdixFile
    
    def delete_file(file_id: int, user_id: str) -> bool
    
    def update_access_level(
        file_id: int,
        access_level: str,
        user_id: str
    ) -> PerdixFile
    
    def increment_download_count(file_id: int) -> None
```

**Responsibilities**:
- File validation (size, type, content)
- Access control checks
- Database record management
- Checksum calculation
- Download tracking
- Soft delete handling

### 5. Schemas (`app/schemas/file.py`)
**Purpose**: Request/response validation

**Schemas**:
```python
# Request Schemas
class FileUploadRequest(BaseModel):
    organization_id: str
    access_level: Literal['public', 'restricted', 'private'] = 'private'

# Response Schemas
class FileResponse(BaseModel):
    id: int
    organization_id: str
    uploaded_by: str
    filename: str
    original_filename: str
    mime_type: str
    file_size: int
    storage_path: str
    checksum: str
    access_level: str
    download_count: int
    created_at: datetime
    # ... other fields

class FileUploadResponse(BaseModel):
    status: str
    message: str
    data: FileResponse
```

### 6. API Endpoints (`app/api/v1/endpoints/files.py`)
**Purpose**: HTTP interface

**Endpoints**:
```
POST   /api/v1/files/upload          - Upload file
GET    /api/v1/files/{file_id}        - Get file metadata
GET    /api/v1/files/{file_id}/download - Download file
DELETE /api/v1/files/{file_id}        - Delete file (soft delete)
PATCH  /api/v1/files/{file_id}/access - Update access level
GET    /api/v1/files/{file_id}/url    - Get presigned URL (for direct S3 access)
```

---

## 🚀 Implementation Strategy

### Phase 1: Foundation (Storage Layer)
1. Add S3 configuration to `config.py`
2. Create `PathBuilder` utility with enums and path generation logic
3. Implement `S3StorageService` with boto3
4. Refactor `LocalStorageService` to match interface
5. Create storage service factory

### Phase 2: Business Logic (Service Layer)
1. Create `FileService` with upload/download logic
2. Integrate `PathBuilder` for hierarchical path generation
3. Implement file validation
4. Add access control checks
5. Implement checksum verification
6. Add context-aware path selection based on file category

### Phase 3: API Layer
1. Create Pydantic schemas
2. Implement API endpoints
3. Add error handling
4. Register router

### Phase 4: Integration
1. Update requirements.txt
2. Add environment variables documentation
3. Test with various file types
4. Add logging

---

## 📁 File Structure

```
app/
├── core/
│   └── config.py                    # ✅ Add S3 config
│
├── utils/
│   └── path_builder.py              # ✅ NEW: Path builder with enums
│
├── services/
│   ├── storage.py                   # ✅ Refactor + Add S3StorageService
│   └── file_service.py              # ✅ NEW: Business logic
│
├── schemas/
│   └── file.py                      # ✅ NEW: Request/response schemas
│
├── api/
│   └── v1/
│       ├── api.py                   # ✅ Register files router
│       └── endpoints/
│           └── files.py             # ✅ NEW: API endpoints
│
└── models/
    └── perdix_file.py               # ✅ Already exists

requirements.txt                     # ✅ Add boto3
.env.example                         # ✅ NEW: Document env vars
```

---

## 🔌 API Design

### 1. Upload File
```http
POST /api/v1/files/upload
Content-Type: multipart/form-data

Form Data:
- file: (binary) - The file to upload
- organization_id: string - Organization ID
- file_category: string - 'KYC' | 'Project' | 'Additional'
- document_type: string - Document type (e.g., 'PAN', 'GST', 'DPR', 'commitment')
- project_reference_id: string (optional) - Required for Project/Additional categories
- access_level: string - 'public' | 'restricted' | 'private' (default: 'private')

Response 201:
{
  "status": "success",
  "message": "File uploaded successfully",
  "data": {
    "id": 123,
    "organization_id": "org-123",
    "uploaded_by": "user-456",
    "filename": "abc123def456.pdf",
    "original_filename": "document.pdf",
    "mime_type": "application/pdf",
    "file_size": 1024000,
    "storage_path": "org-123/KYC/PAN/pan_card_abc123.pdf",
    "checksum": "sha256hash...",
    "access_level": "private",
    "download_count": 0,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### 2. Download File
```http
GET /api/v1/files/{file_id}/download

Headers:
- X-User-Id: string (optional, for access control)

Response 200:
Content-Type: <file_mime_type>
Content-Disposition: attachment; filename="original_filename.pdf"

<binary file content>
```

### 3. Get File Metadata
```http
GET /api/v1/files/{file_id}

Response 200:
{
  "status": "success",
  "data": {
    "id": 123,
    "organization_id": "org-123",
    ...
  }
}
```

### 4. Delete File (Soft Delete)
```http
DELETE /api/v1/files/{file_id}

Response 200:
{
  "status": "success",
  "message": "File deleted successfully"
}
```

### 5. Update Access Level
```http
PATCH /api/v1/files/{file_id}/access
Content-Type: application/json

{
  "access_level": "public"
}

Response 200:
{
  "status": "success",
  "message": "Access level updated",
  "data": { ... }
}
```

### 6. Get Presigned URL (Direct S3 Access)
```http
GET /api/v1/files/{file_id}/url?expires_in=3600

Response 200:
{
  "status": "success",
  "data": {
    "url": "https://bucket.s3.amazonaws.com/path?signature=...",
    "expires_at": "2024-01-15T11:30:00Z"
  }
}
```

---

## 🔒 Security Considerations

### 1. File Validation
- **Size Limits**: Configurable max file size (default: 100MB)
- **Type Validation**: Whitelist allowed extensions
- **Content Validation**: MIME type verification
- **Virus Scanning**: Consider integration (future enhancement)

### 2. Access Control
- **Organization Isolation**: Users can only access files from their organization
- **Access Levels**:
  - `private`: Only uploader and organization admins
  - `restricted`: Organization members
  - `public`: Anyone with file ID
- **Authentication**: Require user context for sensitive operations

### 3. S3 Security
- **IAM Roles**: Use IAM roles with least privilege
- **Bucket Policies**: Restrict public access
- **Encryption**: Enable S3 server-side encryption
- **Presigned URLs**: Time-limited access for direct downloads

### 4. Data Protection
- **Checksum Verification**: SHA-256 for integrity
- **Soft Delete**: Preserve data for recovery
- **Audit Trail**: Track upload/download actions

---

## ✨ Best Practices

### 1. File Naming Strategy
```
Pattern: {organization_id}/{uuid}_{timestamp}.{ext}
Example: org-123/550e8400-e29b-41d4-a716-446655440000_1705312200.pdf

Benefits:
- Unique filenames (UUID)
- Organization isolation
- Timestamp for sorting
- No conflicts
```

### 2. Error Handling
```python
# Specific error types
class FileTooLargeError(Exception): pass
class InvalidFileTypeError(Exception): pass
class FileNotFoundError(Exception): pass
class AccessDeniedError(Exception): pass
class StorageError(Exception): pass
```

### 3. Logging
- Log all file operations (upload, download, delete)
- Include file ID, user ID, organization ID
- Log errors with context
- Track file sizes and types for analytics

### 4. Performance
- **Async Uploads**: Consider async for large files
- **Streaming**: Stream large files instead of loading into memory
- **CDN Integration**: Use CloudFront for public files (future)
- **Caching**: Cache file metadata

### 5. Database Optimization
- Index on `organization_id`, `uploaded_by`, `is_deleted`
- Soft delete queries filter `is_deleted = false`
- Consider partitioning by organization_id for large scale

---

## 📝 Step-by-Step Implementation

### Step 1: Update Configuration
**File**: `app/core/config.py`
- Add S3 settings class
- Add file upload settings
- Load from environment variables

### Step 2: Install Dependencies
**File**: `requirements.txt`
- Add `boto3==1.34.0`
- Add `python-multipart` (if not present)

### Step 3: Implement Storage Service
**File**: `app/services/storage.py`
- Create `StorageServiceInterface` (abstract base)
- Implement `S3StorageService`
- Refactor `LocalStorageService` to match interface
- Create `get_storage_service()` factory function

### Step 4: Create File Service
**File**: `app/services/file_service.py`
- Implement `FileService` class
- Add upload logic with validation
- Add download logic with access control
- Add metadata management methods

### Step 5: Create Schemas
**File**: `app/schemas/file.py`
- `FileUploadRequest`
- `FileResponse`
- `FileUploadResponse`
- `FileAccessUpdate`

### Step 6: Create API Endpoints
**File**: `app/api/v1/endpoints/files.py`
- Implement all 6 endpoints
- Add proper error handling
- Add request validation
- Add response formatting

### Step 7: Register Router
**File**: `app/api/v1/api.py`
- Import files router
- Add to `api_router`

### Step 8: Environment Configuration
**File**: `.env.example` (create if not exists)
- Document all S3 variables
- Document file upload settings

### Step 9: Testing
- Test with various file types (jpg, pdf, video)
- Test access control
- Test error scenarios
- Test large file uploads

---

## 🧪 Testing Strategy

### Unit Tests
- Storage service methods
- File service business logic
- Validation functions

### Integration Tests
- Upload → Download flow
- Access control scenarios
- Database operations
- S3 operations

### Manual Testing Checklist
- [ ] Upload small file (< 1MB)
- [ ] Upload large file (> 10MB)
- [ ] Upload different file types (jpg, pdf, video)
- [ ] Download with valid access
- [ ] Download with invalid access (should fail)
- [ ] Delete file (soft delete)
- [ ] Update access level
- [ ] Get presigned URL
- [ ] Verify checksum integrity
- [ ] Test with missing/invalid S3 credentials

---

## 🔄 Future Enhancements

1. **File Versioning**: Track file versions
2. **Thumbnail Generation**: Auto-generate thumbnails for images
3. **Virus Scanning**: Integrate ClamAV or AWS Macie
4. **CDN Integration**: CloudFront for public files
5. **Batch Operations**: Upload/download multiple files
6. **File Sharing**: Generate shareable links
7. **Compression**: Auto-compress large files
8. **Metadata Extraction**: Extract EXIF, document properties

---

## 📊 Database Considerations

### Indexes to Add
```sql
CREATE INDEX idx_files_org_id ON perdix_mp_files(organization_id);
CREATE INDEX idx_files_uploaded_by ON perdix_mp_files(uploaded_by);
CREATE INDEX idx_files_is_deleted ON perdix_mp_files(is_deleted);
CREATE INDEX idx_files_access_level ON perdix_mp_files(access_level);
```

### Query Optimization
- Always filter by `is_deleted = false` in queries
- Use organization_id for filtering
- Consider pagination for file lists

---

## 🎯 Success Criteria

✅ Files can be uploaded to S3  
✅ Files can be downloaded securely  
✅ Access control works correctly  
✅ File metadata stored in database  
✅ Checksum verification works  
✅ Soft delete implemented  
✅ Error handling comprehensive  
✅ Supports all required file types  
✅ Configuration via environment variables  
✅ Logging in place  

---

## 📚 Additional Resources

- [Boto3 S3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)
- [FastAPI File Upload](https://fastapi.tiangolo.com/tutorial/request-files/)
- [AWS S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)

---

## 🗂️ Hierarchical Folder Structure - Detailed Design

### Overview
The S3 folder structure is designed to organize files logically based on:
1. **Organization** (top-level isolation)
2. **Category** (KYC, Project, Additional)
3. **Context** (project_reference_id, document type)
4. **Document Type** (specific document categories)

### Complete Structure Visualization

```
S3 Bucket Root/
│
└── {org_id}/                                    # Organization-level isolation
    │
    ├── KYC/                                     # KYC Documents Category
    │   ├── PAN/                                 # PAN documents
    │   │   ├── pan_card_abc123.pdf
    │   │   └── pan_card_xyz789.pdf
    │   └── GST/                                 # GST documents
    │       ├── gst_certificate_def456.pdf
    │       └── gst_certificate_ghi012.pdf
    │
    ├── Project/                                 # Project Documents Category
    │   └── {project_reference_id}/              # Dynamic: Project-specific folder
    │       │                                     # Example: PROJ-2024-00001
    │       ├── DPR/                             # Detailed Project Report
    │       │   ├── dpr_v1.pdf
    │       │   └── dpr_v2.pdf
    │       ├── Project Image/                  # Project Images
    │       │   ├── project_image_001.jpg
    │       │   └── project_image_002.jpg
    │       └── Project videos/                 # Project Videos
    │           ├── project_video_001.mp4
    │           └── project_video_002.mp4
    │
    └── Additional/                              # Additional Documents Category
        └── {project_reference_id}/              # Dynamic: Project-specific folder
            │                                     # Example: PROJ-2024-00001
            ├── commitment/                      # Commitment Documents
            │   ├── commitment_letter.pdf
            │   └── sanction_letter.pdf
            └── Requested document/              # Requested Documents
                ├── requested_doc_001.pdf
                └── requested_doc_002.pdf
```

### Path Generation Logic

**Flow Diagram**:
```
API Request
    ↓
Extract: file_category, document_type, project_reference_id (if needed)
    ↓
PathBuilder.build_path()
    ↓
    ├── If KYC → build_kyc_path()
    ├── If Project → build_project_path()
    └── If Additional → build_additional_path()
    ↓
Generated Path: "{org_id}/{category}/{context}/{document_type}/{filename}"
    ↓
Storage Service uploads to S3
    ↓
Path stored in database (perdix_mp_files.storage_path)
```

### Implementation Example

**Scenario 1: Upload KYC PAN Document**
```python
# API receives request
file_category = "KYC"
document_type = "PAN"
org_id = "org-123"

# PathBuilder generates path
path = PathBuilder.build_kyc_path(
    org_id="org-123",
    document_type=KYCDocumentType.PAN,
    filename="pan_card_550e8400.pdf"
)
# Result: "org-123/KYC/PAN/pan_card_550e8400.pdf"

# File uploaded to S3 at that path
# Database stores: storage_path = "org-123/KYC/PAN/pan_card_550e8400.pdf"
```

**Scenario 2: Upload Project DPR Document**
```python
# API receives request
file_category = "Project"
document_type = "DPR"
org_id = "org-123"
project_reference_id = "PROJ-2024-00001"

# PathBuilder generates path
path = PathBuilder.build_project_path(
    org_id="org-123",
    project_reference_id="PROJ-2024-00001",
    document_type=ProjectDocumentType.DPR,
    filename="dpr_document_v1.pdf"
)
# Result: "org-123/Project/PROJ-2024-00001/DPR/dpr_document_v1.pdf"
```

**Scenario 3: Upload Commitment Document**
```python
# API receives request
file_category = "Additional"
document_type = "commitment"
org_id = "org-123"
project_reference_id = "PROJ-2024-00001"

# PathBuilder generates path
path = PathBuilder.build_additional_path(
    org_id="org-123",
    project_reference_id="PROJ-2024-00001",
    document_type=AdditionalDocumentType.COMMITMENT,
    filename="commitment_letter.pdf"
)
# Result: "org-123/Additional/PROJ-2024-00001/commitment/commitment_letter.pdf"
```

### Benefits of This Structure

1. **Organization Isolation**: Each organization's files are completely separated
2. **Logical Grouping**: Files grouped by purpose (KYC, Project, Additional)
3. **Easy Navigation**: Clear folder hierarchy makes finding files intuitive
4. **Scalability**: Structure supports millions of files without performance issues
5. **Access Control**: Can set S3 bucket policies at folder level
6. **Backup/Archive**: Easy to backup specific categories or organizations
7. **Compliance**: Clear audit trail with organized structure

### Extensibility

To add new document types:

1. **Add to Enum**:
```python
class ProjectDocumentType(str, Enum):
    DPR = "DPR"
    PROJECT_IMAGE = "Project Image"
    PROJECT_VIDEOS = "Project videos"
    FEASIBILITY_STUDY = "Feasibility Study"  # NEW
```

2. **PathBuilder automatically handles it** - no code changes needed!

3. **Usage**:
```python
path = PathBuilder.build_project_path(
    org_id="org-123",
    project_reference_id="PROJ-2024-00001",
    document_type=ProjectDocumentType.FEASIBILITY_STUDY,
    filename="feasibility_study.pdf"
)
# Result: "org-123/Project/PROJ-2024-00001/Feasibility Study/feasibility_study.pdf"
```

### Database Integration

The `storage_path` field in `perdix_mp_files` table stores the complete S3 path:
- **Example**: `"org-123/KYC/PAN/pan_card_550e8400.pdf"`
- This allows direct S3 access without additional lookups
- Path can be used to generate presigned URLs
- Path parsing can extract category, document type, etc.

### Migration Strategy

For existing files (if any):
1. Files can be migrated to new structure using batch script
2. Update `storage_path` in database after migration
3. Old paths can be maintained for backward compatibility initially

---

**Ready to proceed?** This plan provides a comprehensive roadmap for implementing the file storage system with hierarchical folder structure. Each component is designed to be modular, testable, and maintainable while following your existing codebase patterns.

