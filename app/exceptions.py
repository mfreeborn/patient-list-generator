class CareFlowError(Exception):
    pass


class NoCareFlowCredentialsError(CareFlowError):
    pass


class CareFlowAuthorisationError(CareFlowError):
    pass


class TrakCareError(Exception):
    pass


class NoTrakCareCredentialsError(TrakCareError):
    pass


class TrakCareAuthorisationError(TrakCareError):
    pass
