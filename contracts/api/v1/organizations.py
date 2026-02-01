from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from application.commands.activate_organization import ActivateOrganizationCommand

router = APIRouter(prefix="/v1/organizations")


@router.patch(
    "/{organization_id}/activate",
    status_code=status.HTTP_200_OK,
)
def activate_organization(
    organization_id: UUID,
    org_service=Depends(get_organization_service),
    current_user=Depends(get_current_user),  # must be ADMIN later
):
    try:
        org = org_service.activate(
            ActivateOrganizationCommand(
                organization_id=organization_id,
                activated_by=current_user.id,
            )
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Organization not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "organization_id": str(org.id),
        "status": org.status,
    }
