'''     try:
            clip = VideoFileClip(file.filename)
            video_length = clip.duration
        except Exception as e:
            return  str(e)
        finally:
            clip.close()

            # Check video length
        if video_length > 70:
            return "Video must be one minute or less"
