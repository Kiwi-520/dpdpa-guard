from .adhaar import ind_adhaar_recognizer
from .pan import ind_pan_recognizer
from .driving_license import ind_driving_licence_recognizer
from .ifsc import ind_ifsc_recognizer
from .passport import ind_passport_number_recognizer
from .upi_id import ind_upi_recognizer
from .vehicle_registration_number import ind_vehicle_registration_number_recognizer
from .voter_id import ind_voter_id_recognizer

ALL_RECOGNIZERS = [
    ind_upi_recognizer,
    ind_adhaar_recognizer,
    ind_pan_recognizer,
    ind_driving_licence_recognizer,
    ind_passport_number_recognizer,
    ind_vehicle_registration_number_recognizer,
    ind_voter_id_recognizer,
    ind_ifsc_recognizer,
]