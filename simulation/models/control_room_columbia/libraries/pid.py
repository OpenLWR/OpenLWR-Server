class PID:
    def __init__(self, Kp, Ki, Kd,minimum,maximum):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.last_error = 0
        self.integral = 0
        self.minimum = minimum
        self.maximum = maximum

    def update(self, setpoint, current, dt):
        error = setpoint-current
        derivative = (error-self.last_error)/dt
        self.integral += error * dt
        output = (self.Kp * error) + (self.Ki * self.integral) + (self.Kd * derivative)
        self.last_error = error
        output = max(min(output,self.maximum),self.minimum) #TODO
        return output
    
class PIDExperimental:
    def __init__(self, Kp, Ki, Kd,minimum,maximum):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.error = 0
        self.proportional = 0
        self.derivative = 0
        self.last_error = 0
        self.integral = 0
        self.minimum = minimum
        self.maximum = maximum

    def reset(self):
        self.error = 0
        self.derivative = 0
        self.last_error = 0
        self.integral = 0

    def update(self, setpoint, current, dt):
        error = setpoint-current
        derivative = (error -self.last_error)/dt
        self.integral += error  * dt * self.Ki
        output = (self.Kp * error ) + (self.integral) + (self.Kd * derivative)
        self.last_error = self.Kd * derivative
        self.error = error
        self.proportional = self.Kp * error
        self.derivative = self.Kd * derivative
        output = max(min(output,self.maximum),self.minimum) #TODO
        return output