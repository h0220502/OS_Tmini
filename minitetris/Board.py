import pygame, sys, datetime, time
import pygame_menu
from pygame.locals import *
from Piece import *

#               R    G    B
WHITE       = (255, 255, 255)
GRAY        = (185, 185, 185)
BLACK       = (  0,   0,   0)
RED         = (155,   0,   0)
LIGHTRED    = (175,  20,  20)
GREEN       = (  0, 155,   0)
LIGHTGREEN  = ( 20, 175,  20)
BLUE        = (  0,   0, 155)
LIGHTBLUE   = ( 20,  20, 175)
YELLOW      = (155, 155,   0)
LIGHTYELLOW = (175, 175,  20)
DARK_GRAY = (55, 55, 55)


class Board:
    COLLIDE_ERROR = {'no_error' : 0, 'right_wall':1, 'left_wall':2,
                     'bottom':3, 'overlap':4}

    def __init__(self, screen):
        '''
        self.screen = screen
        self.width = 10
        self.height = 20
        self.block_size = 25
        self.init_board()
        self.generate_piece()
        '''

        self.width = 5  # 맵의 좌에서 우로 사이즈
        self.height = 15  # 맵 위에서 아래로 사이즈
        self.block_size = int(25*7/5)  # 바꾸면 맵 블럭크기 변경
        self.status_size = 5
        mini_width = 5  # 맵의 좌에서 우로 사이즈
        mini_height = 15  # 맵 위에서 아래로 사이즈
        mini_block_size = int(25*7/5)  # 바꾸면 맵 블럭크기 변경
        mini_status_size = 5  # 상태 바 사이즈 (블럭의 개수 기준으로 )
        mini_display_width = (mini_width + mini_status_size) * mini_block_size
        self.display_width = mini_display_width
        self.display_height = self.height * self.block_size
        self.screen = pygame.display.set_mode((self.display_width, self.display_height), RESIZABLE)

        self.init_board()  # 보드 생성 메소드 실행
        self.generate_piece()  # 블럭 생성 메소드 실행
        '''
        self.start_status_bar_y = 0
        self.status_width = self.block_size * self.status_size
        self.font_size_small_in = 14
        '''



    def init_board(self):
        self.board = []
        self.score = 0
        self.level = 1
        self.goal = 5
        self.skill = 0
        for _ in range(self.height):
            self.board.append([0]*self.width)

    def generate_piece(self):
        self.piece = Piece()
        self.next_piece = Piece()
        self.piece_x, self.piece_y = 0,-2  #몇번 째 칸에서 블럭이 시작하는가

    def nextpiece(self): # 다음에 나올 블럭 그려주기
        self.piece = self.next_piece
        self.next_piece = Piece()
        self.piece_x, self.piece_y = 0, -2

    def absorb_piece(self):
        for y, row in enumerate(self.piece):
            for x, block in enumerate(row):
                if block:
                    self.board[y+self.piece_y][x+self.piece_x] = block
        self.nextpiece()
        self.score += self.level
        if self.skill < 100:
            self.skill += 2

    #충돌 관련
    def block_collide_with_board(self, x, y):
        # 왼쪽 끝점 기준 (0,0)
        if x < 0: #왼쪽 벽
            return Board.COLLIDE_ERROR['left_wall']
        elif x >= self.width: #가로 길이 넘어가면
            return Board.COLLIDE_ERROR['right_wall']
        elif y >= self.height: #세로 길이 넘어가면
            return Board.COLLIDE_ERROR['bottom']
        elif self.board[y][x]: #블럭이 다 쌓이면..?
            return Board.COLLIDE_ERROR['overlap']
        return Board.COLLIDE_ERROR['no_error']

    def collide_with_board(self, dx, dy):
        for y, row in enumerate(self.piece):
            for x, block in enumerate(row):
                if block:
                    collide = self.block_collide_with_board(x=x+dx, y=y+dy)
                    if collide:
                        return collide
        return Board.COLLIDE_ERROR['no_error']

    # 블럭이 움직일 수 있는 경우 판단
    def can_move_piece(self, dx, dy):
        _dx = self.piece_x + dx
        _dy = self.piece_y + dy
        if self.collide_with_board(dx = _dx, dy = _dy):
            return False
        return True

     # 아래로 한칸 내려가는 것
    def can_drop_piece(self):
        return self.can_move_piece(dx=0, dy=1)


    # 블럭 회전 시도
    def try_rotate_piece(self, clockwise=True):
        self.piece.rotate(clockwise)
        collide = self.collide_with_board(dx=self.piece_x, dy=self.piece_y)
        # 충돌하지 않는 다면 패스
        if not collide:
            pass

        # 왼쪽벽과 충돌하는 경우
        elif collide == Board.COLLIDE_ERROR['left_wall']:
            if self.can_move_piece(dx=1, dy=0):
                self.move_piece(dx=1, dy=0)
            elif self.can_move_piece(dx=2, dy=0):
                self.move_piece(dx=2, dy=0)
            else:
                self.piece.rotate(not clockwise)

        #오른쪽 벽과 충돌하는 경우
        elif collide == Board.COLLIDE_ERROR['right_wall']:
            if self.can_move_piece(dx=-1, dy=0):
                self.move_piece(dx=-1, dy=0)
            elif self.can_move_piece(dx=-2, dy=0):
                self.move_piece(dx=-2, dy=0)
            else:
                self.piece.rotate(not clockwise)
        else:
            self.piece.rotate(not clockwise)

    # 블럭 움직이기
    def move_piece(self, dx, dy):
        #만약 움직이기 가능하다면
        if self.can_move_piece(dx, dy):
            self.piece_x += dx
            self.piece_y += dy

    # 블럭 내리기
    def drop_piece(self):
        if self.can_drop_piece():
            self.move_piece(dx=0, dy=1)
        else:
            self.absorb_piece()
            self.delete_lines()

    # 블럭 완전히 밑으로 내리기(내릴 수 없을때 까지)
    def full_drop_piece(self):
        while self.can_drop_piece():
            self.drop_piece()
        self.drop_piece()

    # 블럭 회전 시키기
    def rotate_piece(self, clockwise=True):
        self.try_rotate_piece(clockwise)

    def pos_to_pixel(self, x, y):
        return self.block_size*x, self.block_size*(y-2)

    def pos_to_pixel_next(self, x, y):
        return self.block_size*x*0.6, self.block_size*(y-2)*0.6

    def delete_line(self, y):
        for y in reversed(range(1, y+1)):
            self.board[y] = list(self.board[y-1])

    #라인 삭제하기
    def delete_lines(self):
        remove = [y for y, row in enumerate(self.board) if all(row)]
        for y in remove:
            # 라인 제거 할때 소리
            line_sound = pygame.mixer.Sound("assets/sounds/Line_Clear.wav")
            line_sound.play()
            # 라인 삭제 실행
            self.delete_line(y)

            # level*10만큼 점수 올려주기
            self.score += 10 * self.level
            # level up 까지 목표 골 수 1만큼 내려주기
            self.goal -= 1

            if self.goal == 0: #만약 골이 0이 된다면
                if self.level < 10: # 레벨이 10보다 작다면
                    self.level += 1 # 레벨 올려주고
                    self.goal = 5 * self.level #레벨 * 5 만큼 골 수 변경
                else: # 레벨 10부터는 골수는 없음 ( - ) 로 표시
                    self.goal = '-'
            if self.level <= 9:
                pygame.time.set_timer(pygame.USEREVENT, (500 - 50 * (self.level-1)))
            else:
                pygame.time.set_time(pygame.USEREVENT, 100)

            self.level_speed() #추가: level증가에 따른 속도 증가

    # 레벨별 스피드 조절
    def level_speed(self):
        if self.level < 10:
            pygame.time.set_timer(pygame.USEREVENT, (600 - 40 * self.level))
        else:
            pygame.time.set_timer(pygame.USEREVENT, (600 - 40 * self.level))

    def game_over(self):
        return sum(self.board[0]) > 0 or sum(self.board[1]) > 0


    # 현재 내려오고 있는 블럭 그려주기
    def draw_blocks(self, array2d, color=WHITE, dx=0, dy=0):
        for y, row in enumerate(array2d):
            y += dy
            if y >= 2 and y < self.height:
                for x, block in enumerate(row):
                    if block:
                        x += dx
                        x_pix, y_pix = self.pos_to_pixel(x, y)
                        tmp = 1
                        while self.can_move_piece(0, tmp):
                            tmp += 1
                        x_s, y_s = self.pos_to_pixel(x, y+tmp-1)



                        pygame.draw.rect(self.screen, self.piece.T_COLOR[7],
                                        (x_pix, y_s, self.block_size, self.block_size))
                        pygame.draw.rect(self.screen, BLACK,
                                        (x_pix, y_s, self.block_size, self.block_size),1)

                        pygame.draw.rect(self.screen, self.piece.T_COLOR[block-1],
                                        (x_pix, y_pix, self.block_size, self.block_size))
                        pygame.draw.rect(self.screen, BLACK,
                                        (x_pix, y_pix, self.block_size, self.block_size), 1)


    def draw_next_piece(self, array2d, color=WHITE): #다음 블럭 그려주기
        for y, row in enumerate(array2d):
            for x, block in enumerate(row):
                if block:
                    x_pix, y_pix = self.pos_to_pixel_next(x,y)
                    pygame.draw.rect(self.screen, self.piece.T_COLOR[block-1],
                                    (x_pix+240, y_pix+65, self.block_size * 0.5, self.block_size * 0.5))
                    pygame.draw.rect(self.screen, BLACK,
                                    (x_pix+240, y_pix+65, self.block_size * 0.5, self.block_size * 0.5),1)
    #보드 내 필요한 내용 틀 넣어주기
    def draw(self):
        now = datetime.datetime.now()
        nowTime = now.strftime('%H:%M:%S')
        self.screen.fill(BLACK)
        for x in range(self.width):
            for y in range(self.height):
                x_pix, y_pix = self.pos_to_pixel(x, y)
                pygame.draw.rect(self.screen, (26,26,26),
                 (x_pix, y_pix, self.block_size, self.block_size))
                pygame.draw.rect(self.screen, BLACK,
                 (x_pix, y_pix, self.block_size, self.block_size),1)
        self.draw_blocks(self.piece, dx=self.piece_x, dy=self.piece_y)
        self.draw_blocks(self.board)
        pygame.draw.rect(self.screen, YELLOW, Rect(250, 0, 350, 450))
        self.draw_next_piece(self.next_piece)
        next_text = pygame.font.Font('assets/Roboto-Bold.ttf', 18).render('NEXT', True, BLACK)
        skill_text = pygame.font.Font('assets/Roboto-Bold.ttf', 18).render('SKILL', True, BLACK)
        skill_value = pygame.font.Font('assets/Roboto-Bold.ttf', 16).render(str(self.skill)+'%', True, BLACK)
        score_text = pygame.font.Font('assets/Roboto-Bold.ttf', 18).render('SCORE', True, BLACK)
        score_value = pygame.font.Font('assets/Roboto-Bold.ttf', 16).render(str(self.score), True, BLACK)
        level_text = pygame.font.Font('assets/Roboto-Bold.ttf', 18).render('LEVEL', True, BLACK)
        level_value = pygame.font.Font('assets/Roboto-Bold.ttf', 16).render(str(self.level), True, BLACK)
        goal_text = pygame.font.Font('assets/Roboto-Bold.ttf', 18).render('GOAL', True, BLACK)
        goal_value = pygame.font.Font('assets/Roboto-Bold.ttf', 16).render(str(self.goal), True, BLACK)
        time_text = pygame.font.Font('assets/Roboto-Bold.ttf', 14).render(str(nowTime), True, BLACK)
        self.screen.blit(next_text, (255, 20))
        self.screen.blit(skill_text, (255, 120))
        self.screen.blit(skill_value, (255, 145))
        self.screen.blit(score_text, (255, 200))
        self.screen.blit(score_value, (255,225))
        self.screen.blit(level_text, (255, 275))
        self.screen.blit(level_value, (255,300))
        self.screen.blit(goal_text, (255, 350))
        self.screen.blit(goal_value, (255,375))
        self.screen.blit(time_text, (255, 430))

    #게임 일시 정지
    def pause(self):
        fontObj = pygame.font.Font('assets/Roboto-Bold.ttf', 32)
        textSurfaceObj = fontObj.render('Paused', True, GREEN)
        textRectObj = textSurfaceObj.get_rect()
        textRectObj.center = (175, 185)
        fontObj2 = pygame.font.Font('assets/Roboto-Bold.ttf', 16)
        textSurfaceObj2 = fontObj2.render('Press p to continue', True, GREEN)
        textRectObj2 = textSurfaceObj2.get_rect()
        textRectObj2.center = (175, 235)

        #스크린에 표시
        self.screen.blit(textSurfaceObj, textRectObj)
        self.screen.blit(textSurfaceObj2, textRectObj2)
        pygame.display.update()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYUP and event.key == K_p: # p 누르면 다시 시작
                    running = False

    # 게임 끝나면 점수 보여줌.
    def GameOver(self):
        fontObj = pygame.font.Font('assets/Roboto-Bold.ttf', 32)
        textSurfaceObj = fontObj.render('Game over', True, GREEN)
        textRectObj = textSurfaceObj.get_rect()
        textRectObj.center = (175, 185)
        fontObj2 = pygame.font.Font('assets/Roboto-Bold.ttf', 16)
        textSurfaceObj2 = fontObj2.render('Press a key to continue', True, GREEN)
        textRectObj2 = textSurfaceObj2.get_rect()
        textRectObj2.center = (175, 235)
        self.screen.blit(textSurfaceObj, textRectObj)
        self.screen.blit(textSurfaceObj2, textRectObj2)
        pygame.display.update()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    running = False

    def newGame(self):
        fontObj = pygame.font.Font('assets/Roboto-Bold.ttf', 32)
        textSurfaceObj = fontObj.render('Tetris', True, GREEN)
        textRectObj = textSurfaceObj.get_rect()
        textRectObj.center = (175, 185)
        fontObj2 = pygame.font.Font('assets/Roboto-Bold.ttf', 16)
        textSurfaceObj2 = fontObj2.render('Press a key to continue', True, GREEN)
        textRectObj2 = textSurfaceObj2.get_rect()
        textRectObj2.center = (175, 235)
        self.screen.fill(BLACK)
        self.screen.blit(textSurfaceObj, textRectObj)
        self.screen.blit(textSurfaceObj2, textRectObj2)
        pygame.display.update()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    running = False

    def HS(self, txt="no"):
        if txt != "no":
            fontObj = pygame.font.Font('assets/Roboto-Bold.ttf', 32)
            textSurfaceObj = fontObj.render('HighScore : ' + txt, True, GREEN)
            textRectObj = textSurfaceObj.get_rect()
            textRectObj.center = (175, 185)
            fontObj2 = pygame.font.Font('assets/Roboto-Bold.ttf', 16)
            textSurfaceObj2 = fontObj2.render('Press a key to continue', True, GREEN)
            textRectObj2 = textSurfaceObj2.get_rect()
            textRectObj2.center = (175, 235)
            self.screen.fill(BLACK)
            self.screen.blit(textSurfaceObj, textRectObj)
            self.screen.blit(textSurfaceObj2, textRectObj2)
            pygame.display.update()
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == KEYDOWN:
                        running = False

    def ultimate(self):
        if self.skill == 100:
            bomb = pygame.image.load("assets/images/bomb.jpg")
            bomb = pygame.transform.scale(bomb, (350, 450))
            bomb_sound = pygame.mixer.Sound('assets/sounds/bomb.wav')
            self.screen.blit(bomb, (0, 0))
            pygame.display.update()
            bomb_sound.play()
            time.sleep(1)
            self.board = []
            self.skill = 0
            for _ in range(self.height):
                self.board.append([0]*self.width)
