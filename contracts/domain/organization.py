class InvalidOrganizationState(Exception):
    pass


class Organization:
    ...

    def __init__(self):
        self.status = OrganizationStatus.ACTIVE

    def activate(self):
        if self.status != OrganizationStatus.PENDING:
            raise InvalidOrganizationState(
                f"Cannot activate organization in status {self.status}"
            )
