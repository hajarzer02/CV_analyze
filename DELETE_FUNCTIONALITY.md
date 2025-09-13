# Delete Candidate Functionality

## Overview
The delete candidate functionality allows users to remove candidates and all their associated data from the system through both the backend API and frontend interface.

## Backend Implementation

### API Endpoint
- **URL**: `DELETE /candidates/{candidate_id}`
- **Method**: DELETE
- **Parameters**: 
  - `candidate_id` (path parameter): ID of the candidate to delete

### Response
- **Success (200)**: 
  ```json
  {
    "message": "Candidate {candidate_id} deleted successfully"
  }
  ```
- **Error (404)**: Candidate not found
- **Error (500)**: Server error during deletion

### Implementation Details
1. **Validation**: Checks if candidate exists before deletion
2. **Cascading Delete**: Removes associated job recommendations first (foreign key constraint)
3. **Database Cleanup**: Deletes the candidate record
4. **File Cleanup**: Optionally removes the uploaded CV file from filesystem
5. **Transaction Safety**: Uses database rollback on errors

### Code Location
- File: `main.py`
- Function: `delete_candidate(candidate_id: int, db: Session = Depends(get_db))`

## Frontend Implementation

### API Service
- **File**: `frontend/src/services/api.js`
- **Function**: `deleteCandidate(id)`
- **Method**: Makes DELETE request to `/candidates/{id}`

### Dashboard Component
- **File**: `frontend/src/pages/Dashboard.js`
- **Features**:
  - Delete button in actions column
  - Confirmation modal with candidate details
  - Loading states during deletion
  - Error handling and user feedback
  - Real-time UI updates after deletion

### UI Components

#### Delete Button
- **Location**: Actions column in candidates table
- **Style**: Red button with trash icon
- **Behavior**: Opens confirmation modal

#### Confirmation Modal
- **Trigger**: Clicking delete button
- **Content**: 
  - Warning icon
  - Candidate name
  - Confirmation message
  - Cancel and Delete buttons
- **States**: 
  - Normal: Shows "Delete" button
  - Loading: Shows spinner and "Deleting..." text
  - Disabled: Prevents multiple clicks during deletion

## User Experience Flow

1. **User clicks delete button** → Confirmation modal opens
2. **User sees candidate details** → Modal shows candidate name and warning
3. **User confirms deletion** → Loading state activates
4. **Backend processes deletion** → Database and file cleanup
5. **UI updates automatically** → Candidate removed from table
6. **Modal closes** → User sees updated candidate list

## Security & Safety Features

### Confirmation Required
- Users must explicitly confirm deletion
- Modal prevents accidental deletions
- Clear warning about permanent action

### Data Integrity
- Cascading deletes maintain referential integrity
- Transaction rollback on errors
- Proper error handling and user feedback

### File Management
- Optional file cleanup (with error handling)
- Graceful degradation if file deletion fails
- Warning logs for file deletion issues

## Error Handling

### Backend Errors
- **404**: Candidate not found
- **500**: Database or file system errors
- **Rollback**: Automatic transaction rollback on errors

### Frontend Errors
- **Network errors**: User-friendly error messages
- **Loading states**: Prevents multiple simultaneous deletions
- **UI feedback**: Clear indication of success/failure

## Testing

### Backend Tests
- Delete existing candidate
- Delete non-existent candidate
- Error handling scenarios
- Database integrity verification

### Frontend Tests
- Component integration verification
- API service function availability
- UI element presence and functionality

### Integration Tests
- End-to-end deletion flow
- Database cleanup verification
- File system cleanup verification

## Usage Examples

### Backend API Call
```bash
curl -X DELETE http://localhost:8000/candidates/123
```

### Frontend Usage
```javascript
import { deleteCandidate } from '../services/api';

// Delete a candidate
try {
  await deleteCandidate(candidateId);
  // Update UI
} catch (error) {
  // Handle error
}
```

## Dependencies

### Backend
- FastAPI
- SQLAlchemy
- Database with foreign key constraints

### Frontend
- React
- Lucide React (icons)
- Axios (HTTP client)
- TailwindCSS (styling)

## Future Enhancements

### Potential Improvements
1. **Bulk deletion**: Delete multiple candidates at once
2. **Soft delete**: Mark as deleted instead of permanent removal
3. **Audit trail**: Log deletion actions
4. **Recovery**: Undo deletion within time window
5. **Permissions**: Role-based deletion access

### Configuration Options
1. **File retention**: Keep files after candidate deletion
2. **Cascade options**: Choose what data to delete
3. **Confirmation timeout**: Auto-cancel modal after time
4. **Batch operations**: Process multiple deletions

## Troubleshooting

### Common Issues
1. **Candidate not found**: Verify candidate ID exists
2. **Permission denied**: Check file system permissions
3. **Database errors**: Verify database connection
4. **UI not updating**: Check state management

### Debug Steps
1. Check browser console for errors
2. Verify API endpoint responses
3. Check database for data consistency
4. Verify file system permissions

## Conclusion

The delete functionality provides a complete, user-friendly way to remove candidates from the system while maintaining data integrity and providing clear feedback to users. The implementation includes proper error handling, confirmation dialogs, and cleanup of associated data.
