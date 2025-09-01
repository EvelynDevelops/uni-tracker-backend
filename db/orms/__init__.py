# ORM models package
# Import all ORM models here

from .university import University, Base, UniversityCRUD
from .profiles import Profile, ProfileCRUD
from .student_profile import StudentProfile, StudentProfileCRUD
from .teacher_profile import TeacherProfile, TeacherProfileCRUD
from .parent_links import ParentLink, ParentLinkCRUD
from .teacher_student_links import TeacherStudentLink, TeacherStudentLinkCRUD

__all__ = [
    'University', 'Base', 'UniversityCRUD',
    'Profile', 'ProfileCRUD',
    'StudentProfile', 'StudentProfileCRUD',
    'TeacherProfile', 'TeacherProfileCRUD',
    'ParentLink', 'ParentLinkCRUD',
    'TeacherStudentLink', 'TeacherStudentLinkCRUD'
]