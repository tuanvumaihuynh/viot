package processor

import (
	"fmt"
)

type ParamSetter interface {
	SetBoolV(*bool)
	SetStrV(*string)
	SetLongV(*int)
	SetDoubleV(*float64)
	SetJsonV(map[string]interface{})
}

// setParamValue sets the value of the parameter based on the type of the value
func setParamValue(param ParamSetter, value interface{}) error {
	switch v := value.(type) {
	case bool:
		param.SetBoolV(&v)
	case string:
		param.SetStrV(&v)
	case int:
		param.SetLongV(&v)
	case float32, float64:
		floatValue := float64(v.(float64))
		param.SetDoubleV(&floatValue)
	case map[string]interface{}:
		param.SetJsonV(v)
	default:
		return fmt.Errorf("unsupported data type: %T", v)
	}
	return nil
}
