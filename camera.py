from vimba import *
import time
from pathlib import Path
import cv2


def set_if_writable(feature, value, name=""):
    """Set a Vimba feature if it exists and is writable. Returns True if set."""
    if feature is None:
        return False
    try:
        if feature.is_writable():
            feature.set(value)
            return True
    except Exception as e:
        print(f"[WARN] Failed to set {name or getattr(feature, 'get_name', lambda: 'feature')()}: {e}")
    return False


def configure_gige_transport(cam):
    """
    Optional GigE tuning. These nodes may or may not exist depending on camera.
    If jumbo frames are enabled on your NIC, you can often increase packet size.
    """
    # Typical GenICam node names for GigE Vision:
    if hasattr(cam, "GevSCPSPacketSize"):
        set_if_writable(cam.GevSCPSPacketSize, 9000, "GevSCPSPacketSize")  # only helps if NIC supports jumbo frames
    if hasattr(cam, "GevSCPD"):
        set_if_writable(cam.GevSCPD, 0, "GevSCPD")  # packet delay (us); increase if you see dropped frames


def configure_camera(cam, *, use_external_trigger=False):
    # --- Basic imaging settings ---
    if hasattr(cam, "PixelFormat"):
        set_if_writable(cam.PixelFormat, "Mono8", "PixelFormat")

    # Often good to specify acquisition mode for single-frame grabs (if supported)
    if hasattr(cam, "AcquisitionMode"):
        set_if_writable(cam.AcquisitionMode, "SingleFrame", "AcquisitionMode")

    # Exposure / gain
    if hasattr(cam, "ExposureAuto"):
        set_if_writable(cam.ExposureAuto, "Off", "ExposureAuto")
    if hasattr(cam, "ExposureTime"):
        set_if_writable(cam.ExposureTime, 5000.0, "ExposureTime")  # microseconds

    if hasattr(cam, "GainAuto"):
        set_if_writable(cam.GainAuto, "Off", "GainAuto")
    if hasattr(cam, "Gain"):
        set_if_writable(cam.Gain, 0.0, "Gain")

    # --- ROI ---
    # Many cameras prefer Width/Height first, then offsets.
    for name, val in [("Width", 640), ("Height", 480), ("OffsetX", 0), ("OffsetY", 0)]:
        if hasattr(cam, name):
            set_if_writable(getattr(cam, name), val, name)

    # --- Trigger configuration (choose ONE mode) ---
    if hasattr(cam, "TriggerMode"):
        if use_external_trigger:
            set_if_writable(cam.TriggerMode, "On", "TriggerMode")
            if hasattr(cam, "TriggerSource"):
                set_if_writable(cam.TriggerSource, "Line1", "TriggerSource")
            if hasattr(cam, "TriggerActivation"):
                set_if_writable(cam.TriggerActivation, "RisingEdge", "TriggerActivation")
        else:
            set_if_writable(cam.TriggerMode, "Off", "TriggerMode")

    # --- GigE transport tuning (optional but useful) ---
    configure_gige_transport(cam)


def main():
    save_dir = Path("captures")
    save_dir.mkdir(parents=True, exist_ok=True)

    num_images = 10
    period_s = 1.0  # 1 Hz

    with Vimba.get_instance() as vimba:
        cams = vimba.get_all_cameras()
        if not cams:
            raise RuntimeError("No cameras found (check Vimba Viewer / drivers).")

        with cams[0] as cam:
            configure_camera(cam, use_external_trigger=False)

            next_t = time.monotonic()
            for i in range(num_images):
                # Keep timing stable
                now = time.monotonic()
                if now < next_t:
                    time.sleep(next_t - now)

                frame = cam.get_frame()
                # If you configured Mono8 already, this conversion is usually unnecessary,
                # but keeping it is ok as a safety net.
                try:
                    frame.convert_pixel_format(PixelFormat.Mono8)
                except Exception:
                    pass

                img = frame.as_numpy_ndarray()

                ts = time.strftime("%Y%m%d_%H%M%S")
                out_path = save_dir / f"img_{ts}_{i:03d}.png"
                if not cv2.imwrite(str(out_path), img):
                    raise RuntimeError(f"Failed to write image: {out_path}")

                cv2.imshow("Capture", img)
                cv2.waitKey(1)
                print(f"Captured & saved: {out_path}")

                next_t += period_s

            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
