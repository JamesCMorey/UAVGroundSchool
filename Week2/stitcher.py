import cv2
import os
import argparse

OUT_DIR = "frames_out"

def save_frame(frame, number):
    """Write frame to OUT_DIR for inspection"""
    os.makedirs(OUT_DIR, exist_ok=True) # Ensure the directory exists

    fname = os.path.join(OUT_DIR, f"frame_{number:04d}.jpg")
    cv2.imwrite(fname, frame)


def load_frames(video, save_frames=False, frame_frequency=-1):
    """ Load frames from specified video file and return a list of the
    selected frames. The current implementation makes sure the first and
    last frames of the video are always included in the list.

    PARAMETERS
    video: filename of the video

    save_frames: Boolean for whether to save frames to file in OUT_DIR (useful
        for debugging)

    frame_frequency: how many frames should be skipped between selection
        (ie. 20 -> pick 0th frame, 20th frame, 40th frame)

        frame_frequency will default to a frequency that selects the ~20 frames
        from the video unless otherwise specified.

    RETURN
    Returns list of frames on success
    """

    vid = cv2.VideoCapture(video)
    frame_count = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))

    if frame_frequency == -1:
        frame_frequency = max(1, int(frame_count / 20))

    # Populate frames with selected frames
    frames = []
    frame_num = 0
    rv, frame = vid.read()
    while rv:
        # Save first, last, and every "stepth" frame
        if frame_num % frame_frequency == 0 or frame_num == (frame_count-1):
            frames.append(frame)

        frame_num += 1
        rv, frame = vid.read()

    # Close video file
    vid.release()

    # Save frames to file if specified
    i = 0
    while save_frames and i < len(frames):
        save_frame(frames[i], i)
        i += 1

    return frames

def stitch_aerial(frames):
    """Stitch list of frames using SCANS configuration (primarily for
    aerial / top-down images).

    PARAMETERS
    frames: list of frames to be stitched

    RETURNS
    returns cv2 pano on success
    """

    stitcher = cv2.Stitcher_create(cv2.Stitcher_SCANS)

    status, pano = stitcher.stitch(frames)

    if status != cv2.Stitcher_OK:
        print("Stitching failed, error code:", status)

    return pano


if __name__ == "__main__":
    desc = "Stitch aerial video frames into a panorama"
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("--video", type=str, required=True, help="Path to video file")
    parser.add_argument("--save-frames", action="store_true", help="Save selected frames for inspection")
    parser.add_argument("--output", type=str, default="pano.jpg", help="Output filename for panorama")

    args = parser.parse_args()

    print("Loading frames from video...")
    frames = load_frames(args.video, args.save_frames)

    print("Stitching frames...")
    pano = stitch_aerial(frames)

    print("Writing to file...")
    cv2.imwrite(args.output, pano)

    print("Done.")

