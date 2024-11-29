from moviepy.editor import VideoFileClip, concatenate_videoclips

def concatenate_clips(clip_paths, output_path):
    """ Concatenate multiple video clips into one """
    clips = [VideoFileClip(clip) for clip in clip_paths]
    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_path, codec='libx264')
