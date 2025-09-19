# Admin Functionality for CV Analysis App

This document describes the role-based admin functionality that has been added to the CV Analysis application.

## Overview

The application now supports two user roles:
- **User**: Regular users who can upload CVs, view candidates, and generate recommendations
- **Admin**: Administrators who have additional privileges to manage users

## Features Added

### Backend Changes

#### 1. Database Schema Updates
- Added `role` field to the `User` model with default value 'user'
- Updated all user-related models to include role information

#### 2. Authentication & Authorization
- Added `get_admin_user()` function for admin-only endpoints
- Updated all user responses to include role information
- Implemented role-based access control

#### 3. Admin API Endpoints
- `GET /api/admin/users` - Get all users (admin only)
- `GET /api/admin/users/{user_id}` - Get specific user (admin only)
- `PUT /api/admin/users/{user_id}` - Update user information (admin only)
- `DELETE /api/admin/users/{user_id}` - Delete user (admin only)

#### 4. Security Features
- Admins cannot modify their own role
- Admins cannot delete their own account
- Email uniqueness validation when updating users
- Role validation (only 'user' or 'admin' allowed)

### Frontend Changes

#### 1. New Components
- **AdminPage**: Complete user management interface
- **AdminRoute**: Route guard for admin-only pages

#### 2. Updated Components
- **Navbar**: Shows admin link only for admin users
- **App.js**: Added admin route with proper protection
- **API Service**: Added admin API functions

#### 3. User Interface Features
- User list with role and status indicators
- Edit user modal with form validation
- Delete confirmation dialogs
- Role-based navigation
- Access denied pages for unauthorized users

## Setup Instructions

### 1. Database Migration
The database schema has been updated to include the `role` field. You need to run a migration script to add this column to your existing database.

**Option A: Automated Setup (Recommended)**
```bash
cd backend
.\venv\Scripts\Activate.ps1  # Activate virtual environment
python setup_admin.py
```

**Option B: Manual Setup**
```bash
cd backend
.\venv\Scripts\Activate.ps1  # Activate virtual environment
python migrate_database.py    # Run migration
python create_admin_user.py   # Create admin user
```

### 2. Troubleshooting Migration
If you encounter the error "la colonne users.role n'existe pas" (role column doesn't exist), run the migration script first:

```bash
cd backend
.\venv\Scripts\Activate.ps1
python migrate_database.py
```

This will add the `role` column to your existing users table and set all existing users to have the 'user' role by default.

### 3. Start the Application
```bash
# Backend
cd backend
python main.py

# Frontend (in another terminal)
cd frontend
npm start
```

### 4. Access Admin Panel
1. Login as an admin user
2. Navigate to the "Administration" link in the navbar
3. Or go directly to `/admin`

## Admin Panel Features

### User Management
- **View All Users**: See a complete list of all registered users
- **User Information**: Name, email, role, status, and creation date
- **Edit Users**: Modify name, email, role, and active status
- **Delete Users**: Remove users from the system (with confirmation)
- **Role Management**: Change user roles between 'user' and 'admin'

### Security Measures
- Only admin users can access the admin panel
- Regular users see an "Access Denied" page
- Admins cannot modify their own role
- Admins cannot delete their own account
- Email uniqueness is enforced

## API Documentation

### Admin Endpoints

#### Get All Users
```http
GET /api/admin/users
Authorization: Bearer <admin_token>
```

Response:
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "is_active": true,
    "role": "user",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

#### Update User
```http
PUT /api/admin/users/{user_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Updated Name",
  "email": "updated@example.com",
  "role": "admin",
  "is_active": true
}
```

#### Delete User
```http
DELETE /api/admin/users/{user_id}
Authorization: Bearer <admin_token>
```

## Testing

Run the test script to verify admin functionality:

```bash
python test_admin_functionality.py
```

This will test:
- Admin endpoint protection
- Role-based access control
- User registration
- Authentication flows

## Security Considerations

1. **Token-based Authentication**: All admin endpoints require valid JWT tokens
2. **Role Verification**: Server-side role checking on every admin request
3. **Self-Protection**: Admins cannot modify their own role or delete themselves
4. **Input Validation**: All user inputs are validated and sanitized
5. **Error Handling**: Proper error messages without exposing sensitive information

## Future Enhancements

Potential improvements for the admin functionality:

1. **Bulk Operations**: Select multiple users for bulk actions
2. **User Activity Logs**: Track user actions and changes
3. **Advanced Filtering**: Filter users by role, status, or date
4. **Export Functionality**: Export user data to CSV/Excel
5. **Audit Trail**: Log all admin actions for compliance
6. **User Groups**: Organize users into groups or departments
7. **Permission System**: More granular permissions beyond just user/admin roles

## Troubleshooting

### Common Issues

1. **"Access Denied" for Admin Users**
   - Check if the user's role is set to 'admin' in the database
   - Verify the JWT token is valid and not expired

2. **Admin Panel Not Showing in Navigation**
   - Ensure the user is logged in and has admin role
   - Check browser console for any JavaScript errors

3. **Cannot Create Admin User**
   - Make sure the database is running and accessible
   - Check if the user already exists with the same email

4. **API Errors**
   - Verify the backend server is running on the correct port
   - Check the API base URL in the frontend configuration

### Database Queries

To manually check or modify user roles:

```sql
-- Check all users and their roles
SELECT id, name, email, role, is_active FROM users;

-- Make a user admin
UPDATE users SET role = 'admin' WHERE email = 'user@example.com';

-- Check admin users
SELECT * FROM users WHERE role = 'admin';
```

## Support

If you encounter any issues with the admin functionality, please check:

1. The application logs for error messages
2. The browser console for frontend errors
3. The database connection and schema
4. The JWT token validity and expiration

For additional help, refer to the main application documentation or contact the development team.
