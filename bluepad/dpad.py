import atexit
from time import sleep, time
from threading import Event
from math import atan2, degrees, hypot
from inspect import getfullargspec

from .btcomm import BluetoothServer

class BluePadPosition():
    """
    Represents a position of where the Dpad is pressed, released or held.

    :param float x:
        The x position of the Dpad, 0 being centre, ``-1`` being far left 
        and ``1`` being far right. 

    :param float y:
        The y position of the Dpad, 0 being centre, ``-1`` being at the 
        bottom and ``1`` being at the top. 
    """
    def __init__(self, x, y):
        self._time = time()
        self._x = self._clamped(float(x))
        self._y = self._clamped(float(y))
        self._angle = None
        self._distance = None
        
    def _clamped(self, v):                                                                 
        return max(-1, min(1, v))
    
    @property
    def x(self):
        """
        The x position of the Dpad, ``0`` being centre, ``-1`` being far 
        left and ``1`` being far right. 
        """
        return self._x

    @property
    def y(self):
        """
        The y position of the Dpad, ``0`` being centre, ``-1`` being at 
        the bottom and ``1`` being at the top. 
        """
        return self._y

    @property
    def angle(self):
        """
        The angle from centre of where the Dpad is pressed, held or released.
        0 degress is up, 0 > 180 degrees clockwise, 0 > -180 degrees anti-clockwise.   
        """
        if self._angle == None:
            self._angle = degrees(atan2(self.x, self.y))
        return self._angle

    @property
    def distance(self):
        """
        The distance from centre of where the Dpad is pressed, held or released.
        The radius of the Dpad is ``1``.
        """
        if self._distance == None:
            self._distance = self._clamped(hypot(self.x, self.y))
        return self._distance

    #@property
    #def middle(self):
        #"""
        #Returns ``True`` if the Dpad is pressed, held or released in the middle.
        #"""
        #return True if self.distance <= 0.5 else False

    @property
    def top(self):
        """
        Returns ``True`` if the Dpad is pressed, held or released at the top.
        """
        return True if self.distance > 0.5 and self.angle > -45 and self.angle <= 45 else False
    
    @property
    def right(self):
        """
        Returns ``True`` if the Dpad is pressed, held or released on the right.
        """
        return True if self.distance > 0.5 and self.angle > 45 and self.angle <= 135 else False

    @property
    def bottom(self):
        """
        Returns ``True`` if the Dpad is pressed, held or released at the bottom.
        """        
        return True if self.distance > 0.5 and (self.angle > 135 or self.angle <= -135) else False

    @property
    def left(self):
        """
        Returns ``True`` if the Dpad is pressed, held or released on the left.
        """        
        return True if self.distance > 0.5 and self.angle > -135 and self.angle <= -45 else False

    @property
    def time(self):
        """
        The time the Dpad was at this position.

        Note - this is the time the message was received from the Blue Dot app, 
        not the time it was sent.
        """
        return self._time

class BluePadInteraction():
    """
    Represents an interaction with the Dpad, from when it was pressed to 
    when it was released.

    A ``BluePadInteraction`` can be active or inactive, i.e. it is active 
    because the Dpad has not been released, or inactive because the Dpad
    was released and the interaction finished.

    :param BluePadPosition pressed_position:
        The BluePadPosition when the Dpad was pressed.
    """
    def __init__(self, pressed_position):
        self._active = False
        self._positions = []
        self._positions.append(pressed_position)

    @property
    def active(self):
        """
        Returns ``True`` if the interaction is still active, i.e. the Dpad 
        hasnt been released.
        """
        return self._active

    @property
    def positions(self):
        """
        A list of ``BluePadPositions`` for all the positions which make up this
        interaction.

        The first position is where the Dpad was pressed, the last is where
        the Dpad was released, all position in between are where the position
        Dpad changed (i.e. moved) when it was held down.
        """
        return self._positions

    @property
    def pressed_position(self):
        """
        Returns the position when the Dpad was pressed i.e. where the 
        interaction started.
        """
        return self._positions[0]

    @property
    def released_position(self):
        """
        Returns the position when the Dpad was released i.e. where the 
        interaction ended.

        If the interaction is still active it returns ``None``.
        """
        if not self.active:
            return self._positions[-1]
        else:
            return None

    @property
    def current_position(self):
        """
        Returns the current position for the interaction.

        If the interaction is inactive, it will return the position when the
        Dpad was released
        """
        return self._positions[-1]

    @property
    def duration(self):
        """
        Returns the duration in seconds of the interaction, i.e. the amount time 
        between when the Dpad was pressed and now or when it was released.
        """
        if self.active:
            return time() - self.pressed_position.time
        else:
            return self.released_position.time - self.pressed_position.time

    @property
    def distance(self):
        """
        Returns the total distance of the Dbad interaction
        """
        dist = 0
        for i in range(1, len(self._positions)):
            p1 = self._positions[i-1]
            p2 = self._positions[i]
            dist += hypot(p2.x - p1.x, p2.y - p1.y)

        return dist

    def moved(self, moved_position):
        """
        Adds an additional position to the interaction, called when the position 
        the Dpad is pressed moves.
        """
        if self._active:
            self._positions.append(moved_position)
            
    def released(self, released_position):
        """
        Called when the Dpad is released and completes a Dpad interaction

        :param BluePadPosition released_position:
            The BluePadPosition when the Dpad was released.
        """
        self._active = False
        self._positions.append(released_position)

class BlueBttnPosition():
    """
    Represents a position of where the Buttons are pressed, released or held.

    :param float x:
        The x position of the Buttons, 0 being centre, ``-1`` being far left 
        and ``1`` being far right. 

    :param float y:
        The y position of the Buttons, 0 being centre, ``-1`` being at the 
        bottom and ``1`` being at the top. 
    """
    def __init__(self, x, y):
        self._time = time()
        self._x = self._clamped(float(x))
        self._y = self._clamped(float(y))
        self._angle = None
        self._distance = None
        
    def _clamped(self, v):                                                                 
        return max(-1, min(1, v))
    
    @property
    def x(self):
        """
        The x position of the Buttons, ``0`` being centre, ``-1`` being far 
        left and ``1`` being far right. 
        """
        return self._x

    @property
    def y(self):
        """
        The y position of the Buttons, ``0`` being centre, ``-1`` being at 
        the bottom and ``1`` being at the top. 
        """
        return self._y

    @property
    def angle(self):
        """
        The angle from centre of where the Buttons are pressed, held or released.
        0 degress is up, 0 > 180 degrees clockwise, 0 > -180 degrees anti-clockwise.   
        """
        if self._angle == None:
            self._angle = degrees(atan2(self.x, self.y))
        return self._angle

    @property
    def distance(self):
        """
        The distance from centre of where the Buttons are pressed, held or released.
        The radius of the Buttons is ``1``.
        """
        if self._distance == None:
            self._distance = self._clamped(hypot(self.x, self.y))
        return self._distance

    #@property
    #def middle(self):
        #"""
        #Returns ``True`` if the Blue Dot is pressed, held or released in the middle.
        #"""
        #return True if self.distance <= 0.5 else False

    @property
    def triangle(self):
        """
        Returns ``True`` if the Triangle is pressed, held or released at the top.
        """
        return True if self.distance > 0.5 and self.angle > -45 and self.angle <= 45 else False
    
    @property
    def circle(self):
        """
        Returns ``True`` if the Circle is pressed, held or released on the right.
        """
        return True if self.distance > 0.5 and self.angle > 45 and self.angle <= 135 else False

    @property
    def eks(self):
        """
        Returns ``True`` if the X is pressed, held or released at the bottom.
        """        
        return True if self.distance > 0.5 and (self.angle > 135 or self.angle <= -135) else False

    @property
    def square(self):
        """
        Returns ``True`` if the Square is pressed, held or released on the left.
        """        
        return True if self.distance > 0.5 and self.angle > -135 and self.angle <= -45 else False

    @property
    def time(self):
        """
        The time the Buttons were at this position.

        Note - this is the time the message was received from the BluPad app, 
        not the time it was sent.
        """
        return self._time   

class BlueBttnInteraction():
    """
    Represents an interaction with the Buttons, from when it was pressed to 
    when it was released.

    A ``BlueBttnInteraction`` can be active or inactive, i.e. it is active 
    because the Buttons had not been released, or inactive because the Buttons
    were released and the interaction finished.

    :param BlueBttnPosition pressed_position:
        The BlueBttnPosition when the Buttons were pressed.
    """
    def __init__(self, pressed_position):
        self._active = False
        self._positions = []
        self._positions.append(pressed_position)

    @property
    def active(self):
        """
        Returns ``True`` if the interaction is still active, i.e. the Buttons 
        have not been released.
        """
        return self._active

    @property
    def positions(self):
        """
        A list of ``BlueBttnPositions`` for all the positions which make up this
        interaction.

        The first position is where the Buttons were pressed, the last is where
        the Buttons were released, all position in between are where the position
        Buttons changed (i.e. moved) when they were held down.
        """
        return self._positions

    @property
    def pressed_position(self):
        """
        Returns the position when the Buttons were pressed i.e. where the 
        interaction started.
        """
        return self._positions[0]

    @property
    def released_position(self):
        """
        Returns the position when the Buttons were released i.e. where the 
        interaction ended.

        If the interaction is still active it returns ``None``.
        """
        if not self.active:
            return self._positions[-1]
        else:
            return None

    @property
    def current_position(self):
        """
        Returns the current position for the interaction.

        If the interaction is inactive, it will return the position when the
        Buttons were released
        """
        return self._positions[-1]

    @property
    def duration(self):
        """
        Returns the duration in seconds of the interaction, i.e. the amount time 
        between when the Buttons were pressed and now or when it was released.
        """
        if self.active:
            return time() - self.pressed_position.time
        else:
            return self.released_position.time - self.pressed_position.time

    @property
    def distance(self):
        """
        Returns the total distance of the Buttons interaction
        """
        dist = 0
        for i in range(1, len(self._positions)):
            p1 = self._positions[i-1]
            p2 = self._positions[i]
            dist += hypot(p2.x - p1.x, p2.y - p1.y)

        return dist

    def moved(self, moved_position):
        """
        Adds an additional position to the interaction, called when the position 
        the Buttons are pressed moves.
        """
        if self._active:
            self._positions.append(moved_position)
            
    def released(self, released_position):
        """
        Called when the Buttons are released and completes a Button interaction

        :param BlueBttnPosition released_position:
            The BlueBttnPosition when the Buttons were released.
        """
        self._active = False
        self._positions.append(released_position)
        
class BluePad():
    """
    Interacts with a BluePad client application, communicating when and where it
    has been pressed, released or held.   

    This class starts an instance of a bluetooth server (btcomm.BluetoothServer) 
    which manages the connection with the BluePad client.

    This class is intended for use with the BluePad client application.

    The following example will print a message when the BluePad is pressed::
    
        from bluepad import BluePad
        bp = BluePad()
        bp.wait_for_press()
        print("The bluePad was pressed")

    :param string device:
        The bluetooth device the server should use, the default is ``hci0``, if
        your device only has 1 bluetooth adapter this shouldn't need to be changed.

    :param int port:
        The bluetooth port the server should use, the default is ``1``, and under 
        normal use this should never need to change.

    :param bool auto_start_server:
        If ``True`` (the default), the bluetooth server will be automatically started
        on initialisation, if ``False``, the method ``start`` will need to use called
        before connections will be accepted.
    
    :param bool power_up_device:
        If ``True``, the bluetooth device will be powered up (if required) when the 
        server starts. The default is ``False``. 
        
        Depending on how bluetooth has been powered down, you may need to use rfkill 
        to unblock bluetooth to give permission to bluez to power on bluetooth::

            sudo rfkill unblock bluetooth

    :param bool print_messages:
        If ``True`` (the default), server status messages will be printed stating
        when the server has started and when clients connect / disconect.

    """
    def __init__(self, 
        device = "hci0", 
        port = 1,
        auto_start_server = True,
        power_up_device = False,
        print_messages = True):
        
        self._data_buffer = ""
        self._device = device
        self._port = port
        self._power_up_device = power_up_device
        self._print_messages = print_messages

        self._is_connected_event = Event()
        self._is_pressed_event = Event()
        self._is_released_event = Event()
        self._is_moved_event = Event()
        #self._is_swiped_event = Event()
        self._is_double_pressed_event = Event()

        self._when_pressed = None
        self._when_double_pressed = None
        self._when_released = None
        self._when_moved = None
        #self._when_swiped = None
        self._when_client_connects = None
        self._when_client_disconnects = None

        self._position = None
        self._interaction = None
        self._double_press_time = 0.3

        self._create_server()

        if auto_start_server:
            self.start()

    @property
    def device(self):
        """
        The bluetooth device the server is using. This defaults to ``hci0``.
        """
        return self._device
    
    @property
    def port(self):
        """
        The port the server is using. This defaults to ``1``.
        """
        return self._port

    @property
    def server(self):
        """
        The ``btcomm.BluetoothServer`` instance that is being used to communicate
        with clients.
        """
        return self._server

    @property
    def is_connected(self):
        """
        Returns ``True`` if a BluePad client is connected.
        """
        return self._is_connected_event.is_set()

    @property
    def is_pressed(self):
        """
        Returns ``True`` if the BluePad is pressed (or held).
        """
        return self._is_pressed_event.is_set()

    @property
    def value(self):
        """
        Returns a ``1`` if the BluePad is pressed, ``0`` if released.
        """
        return 1 if self.is_pressed else 0
        
    @property
    def values(self):
        """
        Returns an infinite generator constantly yielding the current value
        """
        while True:
            yield self.value

    @property
    def position(self):
        """
        Returns an instance of ``BluePadPosition`` representing the 
        current or last position the BluePad was pressed, held or 
        released. 
        
        Note - if the BluePad is released (and inactive), ``position`` 
        will return position when it was released, until it is pressed 
        again. If the BluePad has never been pressed ``position`` will
        return ``None``.
        """
        return self._position

    @property
    def interaction(self):
        """
        Returns an instance of ``BluePadInteraction`` representing the 
        current or last interaction with the Blue Dot. 
        
        Note - if the BluePad is released (and inactive), ``interaction`` 
        will return the interaction when it was released, until it is 
        pressed again. If the BluePad has never been pressed ``interaction`` 
        will return ``None``.
        """
        return self._interaction

    @property
    def when_pressed(self):
        """
        Sets or returns the function which is called when the Blue Dot is pressed. 

        The function should accept 0 or 1 parameters, if the function accepts 1 parameter an 
        instance of ``BluePadPosition`` will be returned representing where the BluePad was pressed.
        
        The following example will print a message to the screen when the button is pressed::
        
            from bluepad import BluePad
            
            def Pad_was_pressed():
                print("The BluePad was pressed")
                
            bp = BluePad()
            bp.when_pressed = dpad_was_pressed
            
        This example shows how the position of where the dot was pressed can be obtained::
        
            from bluepad import BluePad
            
            def dot_was_pressed(pos):
                print("The BluePad was pressed at pos x={} y={}".format(pos.x, pos.y))
                
            bp = BluePad()
            bp.when_pressed = dpad_was_pressed

        """
        return self._when_pressed

    @when_pressed.setter
    def when_pressed(self, value):
        self._when_pressed = value

    @property
    def when_double_pressed(self):
        """
        Sets or returns the function which is called when the BluePad is double pressed. 

        The function should accept 0 or 1 parameters, if the function accepts 1 parameter an 
        instance of ``BluePadPosition`` will be returned representing where the BluePad was 
        pressed the second time.

        Note - the double press event is fired before the 2nd press event e.g. events would be 
        appear in the order, pressed, released, double pressed, pressed.
        """
        return self._when_double_pressed

    @when_double_pressed.setter
    def when_double_pressed(self, value):
        self._when_double_pressed = value

    @property 
    def double_press_time(self):
        """
        Sets or returns the time threshold in seconds for a double press. Defaults to ``0.3``.
        """
        return self._double_press_time

    @double_press_time.setter
    def double_press_time(self, value):
        self._double_press_time = value

    @property 
    def when_released(self):
        """
        Sets or returns the function which is called when the BluePad is released. 

        The function should accept 0 or 1 parameters, if the function accepts 1 parameter an 
        instance of ``BluePadPosition`` will be returned representing where the BluePad was held 
        when it was released.
        """
        return self._when_released

    @when_released.setter
    def when_released(self, value):
        self._when_released = value

    @property
    def when_moved(self):
        """
        Sets or returns the function which is called when the position the BluePad is pressed is moved. 

        The function should accept 0 or 1 parameters, if the function accepts 1 parameter an 
        instance of ``BluePadPosition`` will be returned representing the new position of where the 
        Blue Dot is held.
        """
        return self._when_moved

    @when_moved.setter
    def when_moved(self, value):
        self._when_moved = value

    #@property
    #def when_swiped(self):
        #"""
        #Sets or returns the function which is called when the Blue Dot is swiped. 

        #The function should accept 0 or 1 parameters, if the function accepts 1 parameter an 
        #instance of ``BlueDotSwipe`` will be returned representing the how the Blue Dot was
        #swiped.
        #"""
        #return self._when_swiped

    #@when_swiped.setter
    #def when_swiped(self, value):
        #self._when_swiped = value

    @property 
    def when_client_connects(self):
        """
        Sets or returns the function which is called when a BluePad connects. 
        """
        return self._when_client_connects

    @when_client_connects.setter
    def when_client_connects(self, value):
        self._when_client_connects = value

    @property 
    def when_client_disconnects(self):
        """
        Sets or returns the function which is called when a BluePad disconnects. 
        """
        return self._when_client_disconnects

    @when_client_disconnects.setter
    def when_client_disconnects(self, value):
        self._when_client_disconnects = value

    @property
    def print_messages(self):
        """
        When set to ``True`` results in messages relating to the status of the bluetooth server
        to be printed.
        """
        return self._print_messages

    @print_messages.setter
    def print_messages(self, value):
        self._print_messages = value

    def start(self):
        """
        Start the BluetoothServer if it is not already running. By default the server is started at
        initialisation.
        """            
        self._server.start()
        self._print_message("Server started {}".format(self.server.server_address))
        self._print_message("Waiting for connection")

    def _create_server(self):
        self._server = BluetoothServer(
                self._data_received, 
                when_client_connects = self._client_connected,
                when_client_disconnects = self._client_disconnected,
                device = self.device,
                port = self.port,
                power_up_device = self._power_up_device,
                auto_start = False)

    def stop(self):
        """
        Stop the bluetooth server.
        """
        self._server.stop()

    def wait_for_connection(self, timeout = None):
        """
        Waits until a BluePad client connects. 
        Returns ``True`` if a client connects. 

        :param float timeout:
            Number of seconds to wait for a wait connections, if ``None`` (the default), 
            it will wait indefinetly for a connection from a Blue Dot client.
        """
        return self._is_connected_event.wait(timeout)

    def wait_for_press(self, timeout = None):
        """
        Waits until a BluePad is pressed. 
        Returns ``True`` if the BluePad was pressed. 

        :param float timeout:
            Number of seconds to wait for a BluePad to be pressed, if ``None``
            (the default), it will wait indefinetly.
        """
        return self._is_pressed_event.wait(timeout)

    def wait_for_double_press(self, timeout = None):
        """
        Waits until a BluePad is double pressed. 
        Returns ``True`` if the BluePad was double pressed. 

        :param float timeout:
            Number of seconds to wait for a BluePad to be double pressed, if ``None``
            (the default), it will wait indefinetly.
        """
        return self._is_double_pressed_event.wait(timeout)

    def wait_for_release(self, timeout = None):
        """
        Waits until a BluePad is released. 
        Returns ``True`` if the BluePad was released. 

        :param float timeout:
            Number of seconds to wait for a Blue Dot to be released, if ``None`` 
            (the default), it will wait indefinetly.
        """
        return self._is_released_event.wait(timeout)

    def wait_for_move(self, timeout = None):
        """
        Waits until the position where the BluePad is pressed is moved. 
        Returns ``True`` if the position pressed on the BluePad was moved. 

        :param float timeout:
            Number of seconds to wait for the position that the BluePad 
            is pressed to move, if ``None`` (the default), it will wait indefinetly.
        """
        return self._is_moved_event.wait(timeout)

    #def wait_for_swipe(self, timeout = None):
        #"""
        #Waits until the Blue Dot is swiped. 
        #Returns ``True`` if the Blue Dot was swiped. 

        #:param float timeout:
            #Number of seconds to wait for the Blue Dot to be swiped, if ``None``
            #(the default), it will wait indefinetly.
        #"""
        #return self._is_swiped_event.wait(timeout)

    def allow_pairing(self, timeout = 60):
        """
        Allow a Bluetooth device to pair with your Raspberry Pi by Putting the adapter 
        into discoverable and pairable mode.

        :param int timeout:
            The time in seconds the adapter will remain pairable. If set to ``None``
            the device will be discoverable and pairable indefinetly. 
        """
        self.server.adapter.allow_pairing(timeout = timeout)

    def _client_connected(self):
        self._is_connected_event.set()
        self._print_message("Client connected {}".format(self.server.client_address))
        if self.when_client_connects:
            self.when_client_connects()

    def _client_disconnected(self):
        self._is_connected_event.clear()
        self._print_message("Client disconnected")
        if self.when_client_disconnects:
            self.when_client_disconnects()
        
    def _data_received(self, data):
        #add the data received to the buffer
        self._data_buffer += data
        
        #get any full commands ended by \n
        last_command = self._data_buffer.rfind("\n")
        if last_command != -1:
            commands = self._data_buffer[:last_command].split("\n")
            self._process_padcommands(commands)
            self._process_bttncommands(commands)
            #remove the processed commands from the buffer
            self._data_buffer = self._data_buffer[last_command + 1:]

    def _process_padcommands(self, commands):
        for command in commands:
            operation, x, y = command.split(",")
            self._padposition = BluePadPosition(x, y)           
       
            #dpad released
            if operation == "0":
                self._released()
    
            #dpad pressed
            elif operation == "1":
                self._pressed()

            #dpad pressed position moved
            elif operation == "2":
                self._moved()

    def _process_bttncommands(self, commands):
        for command in commands:
            operation, x, y = command.split(",")
            self._bttnposition = BlueBttnPosition(x, y)
                   
            #button released
            if operation == "3":
                self._released()
    
            #button pressed
            elif operation == "4":
                self._pressed()

            #button pressed position moved
            elif operation == "5":
                self._moved()
                

    def _pressed(self):
        self._is_pressed_event.set()
        self._is_released_event.clear()
        self._is_moved_event.clear()

        self._double_pressed()

        #create new interaction
        self._padinteraction = BluePadInteraction(self._padposition)
        self._bttninteraction = BlueBttnInteraction(self._bttnposition)

        self._process_callback(self.when_pressed)

    def _double_pressed(self):
        #was there a previous interaction
        if self._interaction:
            #was it less than the time threshold (0.3 seconds)
            if self._interaction.duration < self._double_press_time:
                #was the dot pressed again in less than the threshold
                if time() - self._interaction.released_position.time < self._double_press_time:
                    self._is_double_pressed_event.set()

                    self._process_callback(self.when_double_pressed)

                    self._is_double_pressed_event.clear()

    def _released(self):
        self._is_pressed_event.clear()
        self._is_released_event.set()
        self._is_moved_event.clear()

        self._padinteraction.released(self._padposition)
        self._bttninteraction.released(self._bttnposition)

        self._process_callback(self.when_released)

        #self._process_interaction()

    def _moved(self):
        self._is_moved_event.set()

        self._padinteraction.moved(self._padposition)
        self._bttninteraction.moved(self._bttnposition)

        self._process_callback(self.when_moved)
    
        self._is_moved_event.clear()
    
    def _process_callback(self, callback):
        if callback:
            if len(getfullargspec(callback).args) == 0:
                callback()
            else:
                callback(self._position)

    #def (self):
        #was the Blue Dot swiped?
        #swipe = BlueDotSwipe(self._interaction)
        #if swipe.valid:
            #self._is_swiped_event.set()
            #if self.when_swiped:
                #if swipe.valid:
                    #if len(getfullargspec(self.when_swiped).args) == 0:
                        #self.when_swiped()
                    #else:
                        #self.when_swiped(swipe)

            #self._is_swiped_event.clear()

    def _print_message(self, message):
        if self.print_messages:
            print(message)
