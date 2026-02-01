class OrganizationService:
    ...

    def activate(self, cmd: ActivateOrganizationCommand):
        org = self.repo.get_by_id(cmd.organization_id)

        if not org:
            raise ValueError("Organization not found")

        org.activate()
        self.repo.update(org)

        self.audit_logger.log(
            action="ORGANIZATION_ACTIVATED",
            resource_id=str(org.id),
            metadata={"activated_by": cmd.activated_by},
        )

        return org
class OrganizationRepository:
    ...

    def get_by_id(self, org_id):
        return (
            self.session.query(OrganizationModel)
            .filter(OrganizationModel.id == org_id)
            .one_or_none()
        )

    def update(self, org):
        self.session.query(OrganizationModel).filter(
            OrganizationModel.id == org.id
        ).update(
            {"status": org.status}
        )
        self.session.commit()
