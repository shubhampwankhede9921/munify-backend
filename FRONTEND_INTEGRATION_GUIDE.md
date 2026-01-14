# Frontend Integration Guide: Project File Upload

## 📋 API Endpoints Summary

### 1. **File Upload API** (Main API for project files)
```
POST /api/v1/projects/files/upload
```

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Headers: `user_id: <user_id>`

**FormData Parameters:**
- `file`: File object (required)
- `document_type`: string (required) - One of: `dpr`, `feasibility_study`, `compliance_certificate`, `budget_approval`, `tender_rfp`, `project_image`, `optional_media`
- `organization_id`: string (required)
- `project_reference_id`: string (optional) - If draft/project exists
- `draft_id`: number (optional) - Alternative to project_reference_id
- `access_level`: string (optional, default: "public") - `public`, `restricted`, or `private`
- `auto_create_draft`: boolean (optional, default: true) - Auto-create draft if project_reference_id doesn't exist

**Response:**
```json
{
  "status": "success",
  "message": "Project file uploaded successfully",
  "data": {
    "file_id": 123,
    "project_document_id": 456,
    "document_type": "dpr",
    "project_reference_id": "PROJ-2024-00001"
  }
}
```

---

### 2. **Delete File API**
```
DELETE /api/v1/projects/files/{file_id}?project_reference_id={project_reference_id}
```

**Request:**
- Method: `DELETE`
- Headers: `user_id: <user_id>`
- Query Params: `project_reference_id` (optional, for validation)

**Response:**
```json
{
  "status": "success",
  "message": "Project file deleted successfully"
}
```

---

### 3. **Create Draft API** (Updated - now returns project_reference_id)
```
POST /api/v1/project-drafts/
```

**Request:**
- Method: `POST`
- Body: `ProjectDraftCreate` (JSON)

**Response:**
```json
{
  "status": "success",
  "message": "Project draft created successfully",
  "data": {
    "id": 123,
    "project_reference_id": "PROJ-2024-00001",  // ⭐ NEW: This is now included!
    // ... other draft fields
  },
  "project_reference_id": "PROJ-2024-00001"  // ⭐ Also at root level for convenience
}
```

---

### 4. **Get Draft API** (Updated - now includes project_reference_id)
```
GET /api/v1/project-drafts/{draft_id}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 123,
    "project_reference_id": "PROJ-2024-00001",  // ⭐ NEW: This is now included!
    // ... other draft fields
  }
}
```

---

## 🎯 Frontend Integration Strategy

### **Option 1: Progressive Upload (Recommended)**
Upload files immediately when user selects them, store `file_id` in form state.

### **Option 2: Batch Upload**
Collect all files, upload them all at once before form submission.

### **Option 3: Upload on Submit**
Upload files only when form is submitted (not recommended for large files).

---

## 📝 Implementation Steps

### **Step 1: Update FormData Interface**

Add file ID fields to your form state:

```typescript
interface FormData {
  // ... existing fields ...
  
  // File objects (for new uploads)
  dprFile: File | null
  feasibilityStudyFile: File | null
  complianceCertificatesFile: File | null
  budgetApprovalsFile: File | null
  tenderRfpFile: File | null
  projectImage: File | null
  optionalMedia: File[]
  
  // File IDs from API (NEW - store these!)
  dprFileId: number | null
  feasibilityStudyFileId: number | null
  complianceCertificatesFileId: number | null
  budgetApprovalsFileId: number | null
  tenderRfpFileId: number | null
  projectImageId: number | null
  optionalMediaIds: number[]
  
  // Project reference ID (NEW - from draft or generated)
  projectReferenceId: string | null
  draftId: number | null
}
```

---

### **Step 2: Create File Upload Mutation**

```typescript
// Using TanStack Query (React Query)
import { useMutation } from '@tanstack/react-query'
import { apiService } from '@/services/api'

const uploadProjectFileMutation = useMutation({
  mutationFn: async ({
    file,
    documentType,
    projectReferenceId,
    draftId,
    organizationId,
  }: {
    file: File
    documentType: string
    projectReferenceId?: string | null
    draftId?: number | null
    organizationId: string
  }) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('document_type', documentType)
    formData.append('organization_id', organizationId)
    formData.append('access_level', 'public')
    formData.append('auto_create_draft', 'true')
    
    // Add project_reference_id or draft_id if available
    if (projectReferenceId) {
      formData.append('project_reference_id', projectReferenceId)
    } else if (draftId) {
      formData.append('draft_id', draftId.toString())
    }
    
    const response = await apiService.post('/projects/files/upload', formData, {
      headers: {
        'user_id': user.id, // Your user ID
        'Content-Type': 'multipart/form-data',
      },
    })
    
    return response.data
  },
  onSuccess: (data) => {
    // Handle success
    console.log('File uploaded:', data.data.file_id)
  },
  onError: (error) => {
    // Handle error
    console.error('Upload failed:', error)
  },
})
```

---

### **Step 3: Update File Change Handler**

```typescript
const handleFileChange = async (
  field: 'projectImage' | 'dprFile' | 'feasibilityStudyFile' | 
         'complianceCertificatesFile' | 'budgetApprovalsFile' | 'tenderRfpFile',
  file: File | null
) => {
  const fieldIdKey = `${field}Id` as keyof FormData
  const existingFileId = formData[fieldIdKey] as number | null
  
  // If replacing existing file, delete old one first
  if (file && existingFileId) {
    try {
      await deleteProjectFileMutation.mutateAsync(existingFileId)
      setFormData(prev => ({ ...prev, [fieldIdKey]: null }))
    } catch (error) {
      console.error('Failed to delete old file:', error)
      // Continue with upload even if delete fails
    }
  }
  
  // Update UI immediately
  setFormData(prev => ({ ...prev, [field]: file }))
  
  // Upload file if provided
  if (file) {
    try {
      // Map field name to document_type
      const documentTypeMap: Record<string, string> = {
        'dprFile': 'dpr',
        'feasibilityStudyFile': 'feasibility_study',
        'complianceCertificatesFile': 'compliance_certificate',
        'budgetApprovalsFile': 'budget_approval',
        'tenderRfpFile': 'tender_rfp',
        'projectImage': 'project_image',
      }
      
      const documentType = documentTypeMap[field] || field
      
      const response = await uploadProjectFileMutation.mutateAsync({
        file,
        documentType,
        projectReferenceId: formData.projectReferenceId,
        draftId: formData.draftId,
        organizationId: user.organizationId,
      })
      
      const fileId = response.data.file_id
      const projectReferenceId = response.data.project_reference_id
      
      // Store file ID and project_reference_id
      setFormData(prev => ({
        ...prev,
        [fieldIdKey]: fileId,
        [field]: null, // Clear File object after successful upload
        projectReferenceId: projectReferenceId || prev.projectReferenceId,
      }))
      
      // Show success message
      toast.success('File uploaded successfully')
    } catch (error) {
      // Remove file on upload failure
      setFormData(prev => ({ ...prev, [field]: null }))
      toast.error('Failed to upload file')
    }
  } else {
    // File removed - delete from server if uploaded
    if (existingFileId) {
      try {
        await deleteProjectFileMutation.mutateAsync(existingFileId)
        setFormData(prev => ({ ...prev, [fieldIdKey]: null }))
        toast.success('File removed successfully')
      } catch (error) {
        console.error('Failed to delete file:', error)
      }
    }
    
    // Clear file ID
    setFormData(prev => ({ ...prev, [fieldIdKey]: null }))
  }
}
```

---

### **Step 4: Update Draft Creation**

When creating a draft, store the `project_reference_id`:

```typescript
const createDraftMutation = useMutation({
  mutationFn: async (draftData: ProjectDraftCreate) => {
    const response = await apiService.post('/project-drafts/', draftData)
    return response.data
  },
  onSuccess: (data) => {
    // Store project_reference_id from response
    setFormData(prev => ({
      ...prev,
      draftId: data.data.id,
      projectReferenceId: data.project_reference_id || data.data.project_reference_id,
    }))
    
    toast.success('Draft saved successfully')
  },
})
```

---

### **Step 5: Update Form Submission**

Include file IDs in your payload:

```typescript
const mapFormDataToDraftPayload = (): ProjectDraftCreate => {
  return {
    // ... existing fields ...
    title: formData.projectTitle || '',
    organization_id: user.organizationId,
    
    // Add file IDs (only if they exist)
    // Note: Backend doesn't expect these in draft payload,
    // but you can include them if your schema supports it
    // Otherwise, files are already linked via project_reference_id
  }
}

const mapFormDataToProjectPayload = (): ProjectCreate => {
  return {
    // ... existing fields ...
    
    // File IDs are already linked via project_reference_id
    // No need to include them in payload
    // Backend will find files by project_reference_id
  }
}
```

---

### **Step 6: Load Existing Files When Editing**

When loading a draft or project, fetch and display existing files:

```typescript
const loadProjectDataIntoForm = async (data: any, isProject: boolean = false) => {
  const item = data?.data || data
  
  if (item && item.id) {
    setFormData(prev => ({
      ...prev,
      // ... existing mappings ...
      
      // Store project_reference_id
      projectReferenceId: item.project_reference_id || null,
      draftId: isProject ? null : item.id,
      
      // Note: File IDs are not returned in project/draft response
      // You may need to fetch them separately if needed
      // Or they're already linked via project_reference_id
    }))
    
    // Optionally: Fetch files for this project_reference_id
    if (item.project_reference_id) {
      // You might need a new API endpoint to get files by project_reference_id
      // Or files are accessible via the project_documents table
    }
  }
}
```

---

## 🔄 Complete Workflow Examples

### **Workflow 1: Create Draft → Upload Files → Submit**

```typescript
// Step 1: Create draft
const draftResponse = await createDraftMutation.mutateAsync({
  organization_id: user.organizationId,
  title: 'My Project',
  // ... other fields
})

// Step 2: Store project_reference_id
const projectReferenceId = draftResponse.project_reference_id
setFormData(prev => ({
  ...prev,
  draftId: draftResponse.data.id,
  projectReferenceId: projectReferenceId,
}))

// Step 3: Upload files (files will use the project_reference_id)
await handleFileChange('dprFile', dprFile)
await handleFileChange('projectImage', imageFile)

// Step 4: Submit draft (files are already linked via project_reference_id)
await submitDraftMutation.mutateAsync(draftResponse.data.id)
```

---

### **Workflow 2: Upload File First → Auto-create Draft**

```typescript
// Step 1: Upload file without draft (auto-creates draft)
const uploadResponse = await uploadProjectFileMutation.mutateAsync({
  file: dprFile,
  documentType: 'dpr',
  organizationId: user.organizationId,
  // No project_reference_id or draft_id provided
})

// Step 2: Store project_reference_id from response
const projectReferenceId = uploadResponse.data.project_reference_id
setFormData(prev => ({
  ...prev,
  projectReferenceId: projectReferenceId,
  dprFileId: uploadResponse.data.file_id,
}))

// Step 3: Continue uploading other files
await handleFileChange('projectImage', imageFile)

// Step 4: Create or update draft with project data
// The draft was auto-created, so you might want to update it
await updateDraftMutation.mutateAsync({
  draftId: /* get from somewhere or create new */,
  data: {
    title: 'My Project',
    // ... other fields
  },
})
```

---

### **Workflow 3: Upload File with Draft ID**

```typescript
// Step 1: Create draft
const draftResponse = await createDraftMutation.mutateAsync({
  organization_id: user.organizationId,
  title: 'My Project',
})

// Step 2: Upload file using draft_id
const uploadResponse = await uploadProjectFileMutation.mutateAsync({
  file: dprFile,
  documentType: 'dpr',
  draftId: draftResponse.data.id,  // Use draft_id
  organizationId: user.organizationId,
})

// File is uploaded and linked to the draft's project_reference_id
```

---

## 📍 Where to Make Changes

### **1. CreateProject.tsx / ProjectForm Component**

**Changes needed:**
- Add file ID fields to form state
- Add `projectReferenceId` and `draftId` to form state
- Update `handleFileChange` to call upload API
- Update draft creation to store `project_reference_id`
- Update form submission to include file IDs (if needed)

**File locations to modify:**
```typescript
// State management
const [formData, setFormData] = useState<FormData>({
  // ... existing fields ...
  projectReferenceId: null,  // ADD
  draftId: null,              // ADD
  dprFileId: null,            // ADD
  // ... other file IDs ...
})

// File upload handler
const handleFileChange = async (field, file) => {
  // UPDATE: Call upload API instead of just storing file
}

// Draft creation
const handleSaveDraft = async () => {
  // UPDATE: Store project_reference_id from response
}

// Form submission
const handleSubmit = async () => {
  // UPDATE: Include file IDs if needed (or rely on project_reference_id)
}
```

---

### **2. API Service File**

**Add new API methods:**

```typescript
// api/projects.ts or api/files.ts

export const projectFileApi = {
  // Upload project file
  upload: async (
    file: File,
    documentType: string,
    organizationId: string,
    options?: {
      projectReferenceId?: string
      draftId?: number
      accessLevel?: string
    }
  ) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('document_type', documentType)
    formData.append('organization_id', organizationId)
    formData.append('access_level', options?.accessLevel || 'public')
    formData.append('auto_create_draft', 'true')
    
    if (options?.projectReferenceId) {
      formData.append('project_reference_id', options.projectReferenceId)
    }
    if (options?.draftId) {
      formData.append('draft_id', options.draftId.toString())
    }
    
    return apiService.post('/projects/files/upload', formData, {
      headers: {
        'user_id': getUserId(),
        'Content-Type': 'multipart/form-data',
      },
    })
  },
  
  // Delete project file
  delete: async (fileId: number, projectReferenceId?: string) => {
    const params = projectReferenceId 
      ? `?project_reference_id=${projectReferenceId}`
      : ''
    return apiService.delete(`/projects/files/${fileId}${params}`, {
      headers: {
        'user_id': getUserId(),
      },
    })
  },
}
```

---

### **3. Draft API Service**

**Update to handle project_reference_id:**

```typescript
// api/drafts.ts

export const draftApi = {
  create: async (data: ProjectDraftCreate) => {
    const response = await apiService.post('/project-drafts/', data)
    // Response now includes project_reference_id
    return response.data
  },
  
  get: async (draftId: number) => {
    const response = await apiService.get(`/project-drafts/${draftId}`)
    // Response now includes project_reference_id
    return response.data
  },
  
  // ... other methods
}
```

---

## ⚠️ Important Notes

### **1. File Upload Timing**
- ✅ **Recommended**: Upload files immediately when user selects them
- ✅ Files are saved even if form submission fails
- ✅ Better UX with upload progress
- ✅ Supports draft saving workflow

### **2. Project Reference ID**
- Always store `project_reference_id` in form state
- Use it for all file uploads
- It's generated when draft is created OR when first file is uploaded
- Same ID is used when draft is converted to project

### **3. File IDs vs Project Reference ID**
- Files are linked via `project_reference_id` in the database
- You don't need to send file IDs in project/draft payload
- Backend automatically links files by `project_reference_id`

### **4. Error Handling**
- Handle upload failures gracefully
- Show loading states during upload
- Allow retry on failure
- Clean up failed uploads

### **5. File Deletion**
- When user removes a file, call delete API
- Update form state to remove file ID
- Handle deletion errors gracefully

---

## 🧪 Testing Checklist

- [ ] Create draft → Get `project_reference_id` → Upload file → Verify file linked
- [ ] Upload file without draft → Verify draft auto-created → Verify `project_reference_id` returned
- [ ] Upload file with `draft_id` → Verify file linked to draft's `project_reference_id`
- [ ] Replace file → Verify old file deleted → Verify new file uploaded
- [ ] Delete file → Verify file removed from server
- [ ] Submit draft → Verify files still linked to project
- [ ] Load existing draft → Verify files are accessible
- [ ] Handle upload errors gracefully
- [ ] Show upload progress to user

---

## 📚 API Response Examples

### **File Upload Response:**
```json
{
  "status": "success",
  "message": "Project file uploaded successfully",
  "data": {
    "file_id": 123,
    "project_document_id": 456,
    "document_type": "dpr",
    "project_reference_id": "PROJ-2024-00001"
  }
}
```

### **Draft Creation Response:**
```json
{
  "status": "success",
  "message": "Project draft created successfully",
  "data": {
    "id": 789,
    "project_reference_id": "PROJ-2024-00001",
    "title": "My Project",
    // ... other fields
  },
  "project_reference_id": "PROJ-2024-00001"
}
```

---

## 🚀 Quick Start Code

```typescript
// Example: Complete file upload integration

// 1. Add to your component state
const [projectReferenceId, setProjectReferenceId] = useState<string | null>(null)
const [draftId, setDraftId] = useState<number | null>(null)
const [fileIds, setFileIds] = useState<Record<string, number>>({})

// 2. Upload file function
const uploadFile = async (file: File, documentType: string) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('document_type', documentType)
  formData.append('organization_id', user.organizationId)
  
  if (projectReferenceId) {
    formData.append('project_reference_id', projectReferenceId)
  } else if (draftId) {
    formData.append('draft_id', draftId.toString())
  }
  
  const response = await apiService.post('/projects/files/upload', formData, {
    headers: { 'user_id': user.id },
  })
  
  const { file_id, project_reference_id } = response.data.data
  
  // Store IDs
  setFileIds(prev => ({ ...prev, [documentType]: file_id }))
  if (project_reference_id) {
    setProjectReferenceId(project_reference_id)
  }
  
  return file_id
}

// 3. Use in file input handler
const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
  const file = e.target.files?.[0]
  if (file) {
    await uploadFile(file, 'dpr')
  }
}
```

---

This guide covers all the changes you need to make. The key is to upload files separately using the `/projects/files/upload` API and store the returned `file_id` and `project_reference_id` in your form state.

