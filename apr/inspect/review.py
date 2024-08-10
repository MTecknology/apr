'''
Package Review
'''
# Python
import logging
import pathlib
import tkinter
import tkinter.ttk
import moviepy.editor
import PIL
import PIL.ImageTk

# APR
import apr.config
import apr.common


class VideoReview(tkinter.ttk.Frame):
    '''
    Package Review 'Main Frame'
    '''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.last_clip = None
        self.resize_delay = None

        # Load selected video
        target_dir = pathlib.Path(self.winfo_toplevel().target_dir.get())
        self.video = moviepy.editor.VideoFileClip(
                str(target_dir / self.winfo_toplevel().target_file.get()))

        # Available Clips
        self.clips = tkinter.ttk.Frame(self)
        self.clips.grid(row=0, column=0, sticky='ew')

        # Scrollbar for Clips
        self.scroll = tkinter.ttk.Scrollbar(
                self.clips, orient='horizontal')
        self.cliplist = tkinter.Canvas(
                self.clips, xscrollcommand=self.scroll.set)
        self.cliplist.pack(side='top', fill='x')
        self.scroll.pack(side='top', fill='x')
        self.scroll.config(command=self.cliplist.xview)

        # Clip Buttons
        self.clip_buttons = tkinter.Frame(self.cliplist)
        self.cliplist.create_window(
                (0, 0), window=self.clip_buttons, anchor='nw')
        self.buttons = []
        # Add one button for each clip
        for clip in apr.common.list_wav(self.winfo_toplevel().tempdir.name):
            i = int(clip.split('.')[0])
            button = tkinter.Button(
                    self.clip_buttons, text=str(i), width=4,
                    command=lambda i=i: self.load_frame(i))
            self.buttons.append(button)
            button.pack(side='left')
        self.button_bg = self.buttons[0].cget('background')

        # Update scroll region
        self.clip_buttons.update_idletasks()
        self.cliplist.config(
                scrollregion=self.cliplist.bbox('all'),
                height=self.clip_buttons.winfo_height())

        # Clip Actions
        self.actions = tkinter.Frame(self)
        self.actions.grid(row=2, column=0, sticky='ew')
        # Replay Audio
        self.replay_btn = tkinter.Button(
                self.actions, text='^ Replay Audio', command=self.play_frame)
        self.replay_btn.pack(side='left', fill='both', expand=True)
        # Tag for Training
        for model in apr.config.get('models'):
            button = tkinter.Button(
                    self.actions, text=f'Tag as {model}',
                    command=lambda m=model: self.tag_as(m))
            button.pack(side='left', fill='both', expand=True)

        # Set up video viewer
        self.player = tkinter.ttk.Frame(self)
        self.player.grid(row=3, column=0, sticky='nesw')
        self.player.image = tkinter.Label(self.player)
        self.player.image.pack(fill='both', expand=True)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Show initial frame
        self.after(100, self.load_frame, 1)

        # Resize image when window size changes
        self.parent.bind('<Configure>', self.resize)

        # Use keypress to transition frame
        self.parent.bind('<Left>', self.navigate)
        self.parent.bind('<Right>', self.navigate)
        self.parent.bind('<Home>', self.navigate)
        self.parent.bind('<End>', self.navigate)
        self.parent.bind('<Page_Up>', self.navigate)
        self.parent.bind('<Page_Down>', self.navigate)

    def navigate(self, event):
        '''
        Navigate frame/clip based on keypress
        '''
        if self.last_clip is None:
            return None
        frame_pos = self.last_clip + 1
        match event.keysym:
            # Navigate 1 frame left
            case 'Left':
                if frame_pos > 1:
                    self.load_frame(frame_pos - 1)
            # Navigate 1 frame right
            case 'Right':
                if frame_pos < len(self.buttons):
                    self.load_frame(frame_pos + 1)
            # Navigate 60 frame left
            case 'Prior':
                if frame_pos > 60:
                    self.load_frame(frame_pos - 60)
                elif frame_pos > 1:
                    self.load_frame(1)
            # Navigate 60 frame right
            case 'Next':
                if frame_pos < len(self.buttons) - 60:
                    self.load_frame(frame_pos + 60)
                elif frame_pos < len(self.buttons):
                    self.load_frame(len(self.buttons))
            # Navigate to start
            case 'Home':
                self.load_frame(1)
            # Navigate to end
            case 'End':
                self.load_frame(len(self.buttons))

        # Update scrollbar position
        self.scroll_to(self.last_clip / len(self.buttons))

    def scroll_to(self, pos):
        '''
        Scroll to specific position (0.0 to 1.0)
        '''
        self.cliplist.xview_moveto(pos)
        x0 = self.cliplist.xview()[0]
        x1 = self.cliplist.xview()[1]
        self.scroll.set(x0, x1)

    def resize(self, event):
        '''
        Resize loaded frame
        '''
        if self.last_clip is None:
            return None

        # Cancel any previously scheduled resize
        if self.resize_delay is not None:
            self.after_cancel(self.resize_delay)

        # Schedule a new call to resize_clip after 500ms
        self.resize_delay = self.after(500, self.resize_clip)

    def load_frame(self, frame_pos):
        '''
        Load image from video at <frame_pos> seconds
        '''
        # Reset button background
        if self.last_clip is not None:
            self.buttons[self.last_clip].config(background=self.button_bg)
        # Set background of selected button
        self.buttons[frame_pos - 1].config(background='#66ffee')
        self.last_clip = frame_pos - 1

        # Load frame from video
        clip_frame = self.video.get_frame(frame_pos)
        self.source_frame = PIL.Image.fromarray(clip_frame)
        self.resize_clip()

        # Play audio from clip
        self.play_frame()

        # Update status message
        self.parent.status.config(
                text='Loaded frame #{frame}  (@ {stamp})  from  {file}'.format(
                    frame=frame_pos,
                    stamp=apr.common.format_time(frame_pos),
                    file=self.winfo_toplevel().target_file.get()))

    def resize_clip(self):
        # Get player dimensions and original dimensions
        player_size = (
                self.player.image.winfo_width() - 4,
                self.player.image.winfo_height() - 4)
        scale = min(
                player_size[0] / self.source_frame.width,
                player_size[1] / self.source_frame.height)

        try:
            # Resize image
            resized_frame = self.source_frame.resize(
                    (int(self.source_frame.width * scale),
                     int(self.source_frame.height * scale)),
                    PIL.Image.LANCZOS)

            # Display updated image
            self.image = PIL.ImageTk.PhotoImage(resized_frame)
            self.player.image.config(image=self.image)
            self.player.image.update_idletasks()
        except ValueError:
            pass

    def play_frame(self, event=None):
        '''
        Play the audio file for a selected frame
        '''
        frame_pos = self.last_clip + 1
        wav = pathlib.Path(
                self.winfo_toplevel().tempdir.name) / f'{frame_pos:04d}.wav'
        apr.common.play_audio(wav)

    def tag_as(self, model):
        '''
        Copy (tag) an audio file to a directory (model)
        '''
        # Determine source path
        frame_pos = self.last_clip + 1
        srcdir = self.winfo_toplevel().tempdir.name
        srcpath = f'{srcdir}/{frame_pos:04d}.wav'

        # Determine destination path
        ws = pathlib.Path(apr.config.get('workspace'))
        of = self.winfo_toplevel().target_file.get()
        dstdir = ws / 'train' / model
        dstpath = f'{dstdir}/{of}:F{frame_pos}.wav'

        # Save file to training data
        apr.common.save_as(srcpath, dstpath)
        notice = f'Saved frame #{frame_pos} of {of} to train {model}'
        self.parent.status.config(text=notice)
        logging.info(notice)
