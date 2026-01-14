# Hierarchical S3 Folder Structure - Design Summary

## 🎯 Overview

This document explains the design decisions for implementing a hierarchical folder structure in S3 for organizing files based on organization, category, and document type.

## 📁 Folder Structure

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

## 🏗️ Architecture Components

### 1. Path Builder Utility (`app/utils/path_builder.py`)

**Purpose**: Centralized path generation logic

**Key Features**:
- **Type-safe enums** for all folder and document types
- **Builder methods** for each category (KYC, Project, Additional)
- **Validation** to ensure correct path structure
- **Extensibility** for adding new document types

**Example Code Structure**:
```python
from enum import Enum

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

class PathBuilder:
    @staticmethod
    def build_kyc_path(org_id: str, document_type: KYCDocumentType, filename: str) -> str:
        return f"{org_id}/KYC/{document_type.value}/{filename}"
    
    @staticmethod
    def build_project_path(org_id: str, project_ref_id: str, 
                          document_type: ProjectDocumentType, filename: str) -> str:
        return f"{org_id}/Project/{project_ref_id}/{document_type.value}/{filename}"
    
    @staticmethod
    def build_additional_path(org_id: str, project_ref_id: str,
                             document_type: AdditionalDocumentType, filename: str) -> str:
        return f"{org_id}/Additional/{project_ref_id}/{document_type.value}/{filename}"
```

### 2. Integration with File Service

**Flow**:
1. API receives upload request with `file_category` and `document_type`
2. `FileService` calls appropriate `PathBuilder` method
3. Path is generated based on context
4. File uploaded to S3 at generated path
5. Path stored in database (`perdix_mp_files.storage_path`)

**Example**:
```python
# In FileService.upload_file()
if file_category == FileCategory.KYC:
    storage_path = PathBuilder.build_kyc_path(
        org_id=organization_id,
        document_type=KYCDocumentType.PAN,
        filename=generated_filename
    )
elif file_category == FileCategory.PROJECT:
    storage_path = PathBuilder.build_project_path(
        org_id=organization_id,
        project_reference_id=project_ref_id,
        document_type=ProjectDocumentType.DPR,
        filename=generated_filename
    )
# ... upload to S3
```

## ✅ Design Principles

### 1. **Type Safety**
- Use Python Enums to prevent typos
- IDE autocomplete support
- Compile-time validation

### 2. **Separation of Concerns**
- Path generation logic isolated in `PathBuilder`
- File service focuses on business logic
- Storage service handles S3 operations

### 3. **Extensibility**
- Adding new document types: Just add to enum
- Adding new categories: Add new builder method
- No changes needed in other components

### 4. **Consistency**
- All paths follow same pattern
- Standardized folder names
- Predictable structure

### 5. **Maintainability**
- Single source of truth for path structure
- Easy to update folder names
- Clear documentation

## 🔄 Usage Patterns

### Pattern 1: KYC Document Upload
```python
# Request includes:
file_category = "KYC"
document_type = "PAN"

# Path generated:
path = PathBuilder.build_kyc_path("org-123", KYCDocumentType.PAN, "pan.pdf")
# Result: "org-123/KYC/PAN/pan.pdf"
```

### Pattern 2: Project Document Upload
```python
# Request includes:
file_category = "Project"
document_type = "DPR"
project_reference_id = "PROJ-2024-00001"

# Path generated:
path = PathBuilder.build_project_path(
    "org-123", 
    "PROJ-2024-00001", 
    ProjectDocumentType.DPR, 
    "dpr.pdf"
)
# Result: "org-123/Project/PROJ-2024-00001/DPR/dpr.pdf"
```

### Pattern 3: Additional Document Upload
```python
# Request includes:
file_category = "Additional"
document_type = "commitment"
project_reference_id = "PROJ-2024-00001"

# Path generated:
path = PathBuilder.build_additional_path(
    "org-123",
    "PROJ-2024-00001",
    AdditionalDocumentType.COMMITMENT,
    "commitment.pdf"
)
# Result: "org-123/Additional/PROJ-2024-00001/commitment/commitment.pdf"
```

## 🎨 Benefits

1. **Organization**: Files automatically organized by context
2. **Scalability**: Structure supports millions of files
3. **Security**: Organization-level isolation
4. **Performance**: Efficient S3 operations with clear prefixes
5. **Compliance**: Clear audit trail
6. **Backup**: Easy to backup specific categories
7. **Access Control**: Can set S3 policies at folder level

## 🚀 Implementation Steps

1. **Create Path Builder** (`app/utils/path_builder.py`)
   - Define enums
   - Implement builder methods
   - Add validation

2. **Update File Service** (`app/services/file_service.py`)
   - Integrate PathBuilder
   - Add category-based path selection
   - Update upload logic

3. **Update API Schemas** (`app/schemas/file.py`)
   - Add `file_category` field
   - Add `document_type` field
   - Add `project_reference_id` (optional)

4. **Update API Endpoints** (`app/api/v1/endpoints/files.py`)
   - Accept new fields in upload request
   - Validate required fields based on category
   - Pass context to FileService

5. **Testing**
   - Test each category
   - Test path generation
   - Test edge cases

## 📝 Notes

- **Filename Generation**: Use UUID + timestamp for uniqueness
- **Path Length**: S3 supports up to 1024 characters in key
- **Special Characters**: Avoid special characters in folder names
- **Case Sensitivity**: S3 keys are case-sensitive
- **Slash Handling**: Use forward slashes `/` for folder separation

## 🔮 Future Enhancements

1. **Versioning**: Add version folders (e.g., `DPR/v1/`, `DPR/v2/`)
2. **Date-based**: Add date folders for better organization
3. **Metadata**: Store folder structure metadata in database
4. **Migration Tool**: Script to reorganize existing files
5. **Validation**: Validate folder structure matches database

---

**This design ensures a clean, maintainable, and scalable file organization system that integrates seamlessly with your FastAPI application.**

