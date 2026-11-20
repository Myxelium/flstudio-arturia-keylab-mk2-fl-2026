# Enable verbose dispatcher logs.
DEBUG = False

# Print the first N raw MIDI events to Script output (helps diagnose mapping).
PROBE_EVENT_LIMIT = 50
_probe_count = 0
_seen_types = set()
_warned_not_mcu = False


def _byte(value, default=-1):
    """Read a MIDI data byte without turning real 0 into -1."""
    if value is None:
        return default
    try:
        return int(value)
    except Exception:
        return default


def log(tag, message, event=None):
    """Log out messages to the script console if global DEBUG variable is True."""
    if DEBUG:
        event_str = _event_as_string(event) if event is not None else '_' * 63
        print('%63s | [%s] %s' % (event_str, tag, message))


def probe(event, prefix='MIDI'):
    """Always print a limited number of incoming events for troubleshooting."""
    global _probe_count, _warned_not_mcu
    _track_protocol(event)
    if _probe_count >= PROBE_EVENT_LIMIT:
        if not _warned_not_mcu:
            _maybe_warn_not_mcu()
        return
    _probe_count += 1
    try:
        print('%s #%d %s' % (prefix, _probe_count, _event_as_string(event)))
    except Exception as e:
        print('%s #%d <unprintable: %s>' % (prefix, _probe_count, e))


def _track_protocol(event):
    status = _byte(getattr(event, 'status', None), 0)
    msg_type = status & 0xF0
    if msg_type == 0x90 or msg_type == 0x80:
        _seen_types.add('note')
    elif msg_type == 0xE0:
        _seen_types.add('pitchbend')
    elif msg_type == 0xB0:
        _seen_types.add('cc')
    else:
        _seen_types.add('other')


def _maybe_warn_not_mcu():
    global _warned_not_mcu
    _warned_not_mcu = True
    if 'note' in _seen_types or 'pitchbend' in _seen_types:
        print('PROTOCOL OK: saw MCU-like note/pitch-bend messages.')
        return
    if 'cc' in _seen_types:
        print('=' * 72)
        print('PROTOCOL WARNING: MIDIIN2 is only receiving Control Changes (CC).')
        print('Mackie/MCU Play/Stop/Faders use Note On + Pitch Bend, not CC.')
        print('Fix on the KeyLab:')
        print('  1) Press DAW so DAW mode is active (not User / Analog Lab).')
        print('  2) Hold DAW for 1 second, turn jog to "Standard MCU" / Default MCU,')
        print('     press jog to confirm.')
        print('  3) In MIDI Control Center > Device settings, set DAW map = Default MCU,')
        print('     store to device, then quit MCC.')
        print('Then press Play again — you should see status=144 (notes) and/or 224+ (faders).')
        print('=' * 72)


def _event_as_string(event):
    """Convert a midi event packet to a string representation."""
    return '[id, status, cnum, cval, d1, d2] = %3d, %3d, %3d, %3d, %3d, %3d' % (
        _byte(getattr(event, 'midiId', None)),
        _byte(getattr(event, 'status', None)),
        _byte(getattr(event, 'controlNum', None)),
        _byte(getattr(event, 'controlVal', None)),
        _byte(getattr(event, 'data1', None)),
        _byte(getattr(event, 'data2', None)),
    )
