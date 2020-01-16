class CareFlowError(Exception):
    pass


class NoCareFlowCredentialsError(CareFlowError):
    pass


class CareFlowAuthorisationError(CareFlowError):
    pass
