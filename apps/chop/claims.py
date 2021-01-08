from apps.oidc.claims import BaseProvider
from ..accounts.models import PersonToPersonRelationship
import logging


logger = logging.getLogger('verifymyidentity.%s' % __name__)


class PersonToPersonClaimProvider(BaseProvider):
    # For family relationships between people (members/patients)

    def claim_person_to_person(self):
        response = []
        try:
            p2p = PersonToPersonRelationship.objects.filter(delegate=self.user)
            for p in p2p:
                response.append(p.structured_response())
            return response
        except Exception as e:
            logger.debug(e)
            return response
