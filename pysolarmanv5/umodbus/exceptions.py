from umodbus.exceptions import ModbusError, error_code_to_exception_map

class NegativeAcknowledgeError(ModbusError):
    """ The server cannot perform the program function received in the query.
    This code is returned for an unsuccessful programming request using
    function code 13 or 14 decimal.
    """
    error_code = 7

    def __str__(self):
        return self.__doc__

error_code_to_exception_map |= {
    NegativeAcknowledgeError.error_code: NegativeAcknowledgeError
}
