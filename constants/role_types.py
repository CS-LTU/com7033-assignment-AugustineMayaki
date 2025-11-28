class RoleTypes:
    SUPER_ADMIN = 'super admin'
    DOCTOR = 'doctor'
    NURSE = 'nurse'

    @staticmethod
    def all_roles():
        """
        Return a list of all defined roles.
        """
        return [RoleTypes.SUPER_ADMIN, RoleTypes.DOCTOR, RoleTypes.NURSE]