import pygame, os, time

class SpriteSheet:
    def __init__(self, filename, colorkey=(0,0,0)):
        self.sheet = pygame.image.load(filename).convert_alpha()
        self.colorkey = colorkey

    def image_at(self, rectangle, colorkey=None):
        "Load a specific image from a specific rectangle"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size, pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), rect)
        return image

    def images_at(self, rects):
        return [self.image_at(rect) for rect in rects]

class AnimatedSprite:
    """
    Lightweight animated sprite helper.
    Usage:
      anim = AnimatedSprite(sprite, 'assets/images/sprites/player_sheet.png', frame_w=32, frame_h=48,
                            animations={'idle':[0,1,2,3], 'run':[6,7,8,9,10,11]}, fps=10)
      # in sprite.update(): call anim.update(); then sprite.image = anim.get_image()
    """
    def __init__(self, owner, filepath, frame_w, frame_h, cols=None, animations=None, fps=8):
        self.owner = owner
        self.filepath = filepath
        self.frame_w = frame_w
        self.frame_h = frame_h
        self.fps = fps
        self.animations = animations or {'idle':[0]}
        self.current_anim = list(self.animations.keys())[0]
        self.current_frame_idx = 0
        self.last_update = pygame.time.get_ticks()
        self.sheet = SpriteSheet(filepath)
        # derive cols from image width if not provided
        if cols is None:
            img_w = self.sheet.sheet.get_width()
            cols = img_w // frame_w
        self.cols = cols
        # pre-slice frames
        self.frames = []
        total_frames = (self.sheet.sheet.get_width()//frame_w) * (self.sheet.sheet.get_height()//frame_h)
        for i in range(total_frames):
            col = i % self.cols
            row = i // self.cols
            rect = (col*frame_w, row*frame_h, frame_w, frame_h)
            self.frames.append(self.sheet.image_at(rect))

    def set_animation(self, name):
        if name == self.current_anim:
            return
        if name in self.animations:
            self.current_anim = name
            self.current_frame_idx = 0
            self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        ms_per_frame = 1000 // max(1, self.fps)
        if now - self.last_update > ms_per_frame:
            self.last_update = now
            frames = self.animations[self.current_anim]
            self.current_frame_idx = (self.current_frame_idx + 1) % len(frames)

    def get_image(self):
        frames = self.animations[self.current_anim]
        idx = frames[self.current_frame_idx] if frames else 0
        # guard: if idx out of range, clamp
        if idx < 0 or idx >= len(self.frames):
            idx = 0
        return self.frames[idx]
