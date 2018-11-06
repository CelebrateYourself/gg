

class Setting():

    METH_PREFIX = '_validate_'

    def __init__(self, *, type, default, widget='entry', **params):
        self._value = None
        self.__dict__.update(params)
        self.widget = widget
        self.type = type
        validator_name = '{}{}'.format(self.METH_PREFIX, self.type)
        self.validator = getattr(self, validator_name)
        self.set(default)

    def is_valid(self, value):
        return self.validator(value)

    def get(self):
        return self._value

    def set(self, value):
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
