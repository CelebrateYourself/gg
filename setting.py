"""Simple validator"""

class Setting():
    """Wrapper over a value and its validator
    
    - type     : used to assign a validator function 
                 from class methods
    - default  : initial value for setting, use set()
    - widget   : name of widget (in view.SettingsDialog)
    - **params : used to transfer data, specific for each 
                 setting
    
    For each type you need to write a validation method 
    named METH_PREFIX_type
    """
    METH_PREFIX = '_validate_'

    def __init__(self, *, type, default, widget='entry', **params):
        self.__dict__.update(params)
        self.type = type
        self._value = None
        self.widget = widget
        validator_name = '{}{}'.format(self.METH_PREFIX, self.type)
        self.validator = getattr(self, validator_name)

        self.set(default)

    def is_valid(self, value):
        return self.validator(value)

    def get(self):
        return self._value

    def set(self, value):
        """Set the value if it is valid"""
        if self.validator(value):
            self._value = value
        else:
            msg = (
                'Setting.set(value): value "{} ({})" '
                'is incorrect for "{}" setting.\nParams:\n{}'
            )
            raise ValueError(
                msg.format(
                    value,
                    type(value),
                    self.type,
                    str(self.__dict__)
                )
            )

    def _validate_range(self, number):
        return number in range(self.from_, self.to+1) # 'to' include in range

    def _validate_bool(self, flag):
        return type(flag) is bool
