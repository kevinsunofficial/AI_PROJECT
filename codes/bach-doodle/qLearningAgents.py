from collections import defaultdict
import numpy as np
import random
import os
import os.path as osp
import re

class qLearningAgent:
    def __init__(self, num_iter=100, alpha=0.5, gamma=1, epsilon=0.5):
        self.num_iter = num_iter
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        # self.actions = []
        self.Q_values = defaultdict(float)
        self.decay = 0.96

    def get_qvalue(self,state,action):
        return self.Q_values[(state,action)]

    def compute_value_from_qvalues(self,state):
        a_s = self.get_legal_actions(state)
        if not a_s: return 0.0
        if len(a_s)==0: return 0.0
        v_max = float("-inf")
        for a in a_s:
          v_max = max(v_max,self.get_qvalue(state,a))
        return v_max

    def compute_action_from_qvalues(self,state):
        q_max = float("-inf")
        a_max = None
        for a in self.get_legal_actions(state):
          if q_max <= self.get_qvalue(state,a):
            q_max = self.get_qvalue(state,a)
            a_max =  a
        return a_max

    def compute_qvalue(self):
        pass

    def get_action(self, state):
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  When there are
          no legal actions, which is the case at the terminal state, we
          choose None as the action.
        """
        legalActions = self.get_legal_actions(state)
        action = None
        # exploration
        if np.random.uniform() < self.epsilon:
        #   print('legal ac',legalActions)
          action = random.choice(legalActions)
        else:
          action = self.compute_action_from_qvalues(state)
        self.epsilon *= self.decay

        return action

    def update(self,state,action,nextState,reward):
        #update self.actions and the qvalues
        q_max =float("-inf")
        if not state.is_end():
            a_s = self.get_legal_actions(nextState)
            for a_next in a_s:
                q_max = max(q_max,self.get_qvalue(nextState,a_next))
            if len(a_s)==0:
                sample = reward
            else:
                sample = reward + self.gamma*q_max
        else:
            # print("?")
            sample = reward
        self.Q_values[(state,action)] = (1-self.alpha)*self.get_qvalue(state,action)+self.alpha*sample
        state.actions.append(self.get_action(state))
        # print('hello',state.actions)
        # print(state.end_time, state.is_end())
        # print('next state', nextState)
        return

    def get_legal_actions(self, state):
        """
        This function returns the legal actions/all the pitches that the agent can choose for the next
        timestamp based on the current state.
        """
        if not state.new_notes:
            # print("???",state.new_notes)
            # return state.new_notes 
            return [state.root]
        else:
            # print('state.root')
            # print("!!!")
            # return [state.root]
            return state.new_notes



class state:
    def __init__(self, start_time, end_time, root, new_notes, notes, actions=[]):
        """
            如果要是下面都建新object了那之前那几个parameter肯定不够啊
            先加上了 不用再删
        """
        self.start_time = start_time
        self.end_time = end_time
        self.notes = notes
        self.root = root
        # a list of integers representing pitches
        self.new_notes = new_notes
        self.actions = actions

    def is_end(self):
        return float(self.end_time) == 8.0


    def get_current_notes(self):
        """
            这个肯定是当前时间点的吧
            __ _*_ __
            但这个是要original pitch还是new pitch啊
            都先return了 再看再删吧
        """
        start, end, notes = self.start_time, self.end_time, self.notes
        current_origin, current_new = notes[(start,end)][0], notes[(start,end)][1]
        return current_origin, current_new

    def get_previous_state(self):
        """
            这个是前一个时间点
            _*_ __ __
            这个是return state哈 那得重新建一个state object 用前一个的parameter
            不是简单的一个note
        """
        start, end, notes = self.start_time, self.end_time, self.notes
        keys = list(notes.keys())
        keys.sort(key=lambda time:time[0])
        timestamp = keys.index((start,end))
        start, end = keys[timestamp-1] if timestamp >= 1 else None
        previous_origin = notes[keys[timestamp-1]][0] if timestamp >= 1 else None
        previous_new = notes[keys[timestamp-1]][1] if timestamp >= 1 else []
        previous_state = state(start,end,previous_origin,previous_new, self.notes)\
             if start != None and end and previous_origin and previous_new !=None else None
        # print("prev state:", previous_state.end_time)
        return previous_state

    def get_next_state(self):
        """
            我以为这个东西才应该是下一个时间点的
            __ __ _*_
            这也应该是个state object吧？既然前面那个都是return的state object
            但notes也make sense所以先return的是notes
            如果后面要class再改
        """
        # if self.is_end():
        #     return state()
        start, end, notes = self.start_time, self.end_time, self.notes
        keys = list(notes.keys())
        keys.sort(key=lambda time:time[0])
        timestamp = keys.index((start,end))
        start, end = keys[timestamp+1] if timestamp < len(keys)-1 else (None, None)
        next_origin = notes[keys[timestamp+1]][0] if timestamp < len(keys)-1 else None
        next_new = notes[keys[timestamp+1]][1] if timestamp < len(keys)-1  else []
        next_state = state(start,end,next_origin,next_new, self.notes, self.actions) if start and end and next_origin and next_new != None else None
        # print('start:',start, 'end:',end, 'next_origin', next_origin, 'next new', next_new)
        # print(next_state)
        return next_state

    def get_next_possible_notes(self):
        """
            我以为这个东西才应该是下一个时间点的
            __ __ _*_
            这也应该是个state object吧？既然前面那个都是return的state object
            但notes也make sense所以先return的是notes
            如果后面要class再改
        """
        # notes = layout.get_notes()
        # return notes[tuple(self.start_time,self.end_time)][1]
        start, end, notes = self.start_time, self.end_time, self.notes
        keys = list(notes.keys())
        keys.sort(key=lambda time:time[0])
        timestamp = keys.index((start,end))
        previous = notes[keys[timestamp+1]][1] if timestamp < len(keys)-1 else None
        return previous


def init_layout(info):
    """
        每次main的时候跑一次
        直接把所有initialize在这里做吧
        layout_info = [
            original note_seq,
            new note_seq
        ]
        每个note_seq都是{start_time(0.0没有),end_time,pitch}需要用 其它key不用

        另外感觉这个self.notes是很重要的 应该是全局的 不应该只在layout里加载

        self.notes structure = {(start_time, end_time):(origin_note_pitch, [new_note_pitch,...])}
    """
    notes = {}
    origin, new = info # origin = ['start,end,pitch',...]
    for n in origin:
        start, end, pitch = n.strip().split(',')
        start, end, pitch = float(start), float(end), int(pitch)
        notes[(start,end)] = (pitch,[])
    for n in new:
        start, end, pitch = n.strip().split(',')
        start, end, pitch = float(start)-8.25, float(end)-8.25, int(pitch)
        for timestamp in notes.keys():
            if timestamp[0] <= start < timestamp[1]:
                notes[timestamp][1].append(pitch)
                break
    return origin, new, notes



def get_major_notes(root):
    major_third = root + 4
    perfect_fifth = root + 7
    second_inversion = [root-8, root-5]
    consonance = [major_third, perfect_fifth, second_inversion[0], second_inversion[1]]
    return consonance

def get_minor_notes(root):
    major_third = root + 3
    perfect_fifth = root + 7
    second_inversion = [root-9, root-5]
    consonance = [major_third, perfect_fifth, second_inversion[0], second_inversion[1]]
    return consonance  

def get_dissonance(root):
    return [root+1, root+2, root-1, root-2, root-11, root-10, root+11, root+10]

#take in two pitch values; root is the original note and pitch is note being evaluated
# using major chords only
def get_major_reward(root, pitch):
    highest_reward = get_major_notes(root)
    dissonance = get_dissonance(root)
    octaves = [root+12, root-12]
    if pitch in highest_reward:
        return 50
    elif pitch in dissonance or pitch == root:
        return -50
    elif pitch in octaves:
        return 10
    elif abs(pitch-root) < 12:
        return 20
    # span more than one octave
    else:
        return -50

def get_minor_reward(root, pitch):
    highest_reward = get_minor_notes(root)
    dissonance = get_dissonance(root)
    octaves = [root+12, root-12]
    if pitch in highest_reward:
        return 50
    elif pitch in dissonance or pitch == root:
        return -50
    elif pitch in octaves:
        return 10
    elif abs(pitch-root) < 12:
        return 20
    # span more than one octave
    else:
        return -50


def get_comparison_reward(root, pitch, prev_root, prev_pitch):
    reward = 0
    pitch_dissonance = get_dissonance(pitch)
    if prev_root in pitch_dissonance or prev_pitch in pitch_dissonance:
        reward -= 40
    if abs(pitch-prev_root) > 12 or abs(pitch-prev_pitch) > 12:
        reward -= 40
    if root == prev_root and pitch == prev_pitch:
        reward -= 10
    consonance = get_major_notes(root)
    consonance.extend([root+12, root-12])
    sub = [ele for ele in consonance if ele in [root, pitch, prev_root, prev_root]]
    if len(sub) == 4:
        reward += 40
    if len(sub) == 3:
        reward += 30
    if (root < max(prev_root, prev_pitch) and root > min(prev_root, prev_pitch)) or (pitch < max(prev_root, prev_pitch) and pitch > min(prev_root, prev_pitch)):
        reward += 10

    return reward


def get_comparison_reward_minor(root, pitch, prev_root, prev_pitch):
    reward = 0
    pitch_dissonance = get_dissonance(pitch)
    if prev_root in pitch_dissonance or prev_pitch in pitch_dissonance:
        reward -= 40
    if abs(pitch-prev_root) > 12 or abs(pitch-prev_pitch) > 12:
        reward -= 40
    if root == prev_root and pitch == prev_pitch:
        reward -= 10
    consonance = get_minor_notes(root)
    consonance.extend([root+12, root-12])
    sub = [ele for ele in consonance if ele in [root, pitch, prev_root, prev_root]]
    if len(sub) == 4:
        reward += 40
    if len(sub) == 3:
        reward += 30
    if (root < max(prev_root, prev_pitch) and root > min(prev_root, prev_pitch)) or (pitch < max(prev_root, prev_pitch) and pitch > min(prev_root, prev_pitch)):
        reward += 10

    return reward

def get_total_reward(root, pitch, prev_root, prev_pitch):
    if pitch is None or prev_pitch is None:
        return 0
    else:
        return max(get_major_reward(root, pitch)+get_comparison_reward(root, pitch, prev_root, prev_pitch),get_minor_reward(root, pitch)+get_comparison_reward_minor(root, pitch, prev_root, prev_pitch))


if __name__ == "__main__":
    input_dir = '/u/ys4aj/YuchenSun/Course/CS4710/AI_PROJECT/codes/bach-doodle/magenta_txt/'
    out_file = '/u/ys4aj/YuchenSun/Course/CS4710/AI_PROJECT/codes/bach-doodle/qlearn_midi/demo.txt'
    # input_dir = 'C:/Users/lin_x/Desktop/UVA/2.3/CS 4710/final_project/AI_PROJECT/codes/bach-doodle/magenta_txt/'
    # out_file = 'C:/Users/lin_x/Desktop/UVA/2.3/CS 4710/final_project/AI_PROJECT/codes/bach-doodle/qlearn_midi/all_selected_try.txt'
    # input_dir = 'C:/KevinSun/University/3rd_year/Classes/Semester1/CS4710/Final/AI_PROJECT/codes/bach-doodle/magenta_txt/'
    # out_file = 'C:/KevinSun/University/3rd_year/Classes/Semester1/CS4710/Final/AI_PROJECT/codes/bach-doodle/qlearn_midi/all_selected.txt'
    all_layouts = {}
    # for name in os.listdir(input_dir):
    #     origin, new = [], []
    #     path = osp.join(input_dir,name)
    #     with open(path,'r') as file:
    #         content = re.split('------------------------\n',file.read())
    #         origin, new = content[0].strip().split('\n'), content[1].strip().split('\n')
    #     layout_info = [origin, new]
    #     all_layouts[name] = layout_info
    for name in os.listdir(input_dir):
        origin, new = [], []
        path = osp.join(input_dir,name)
        with open(path,'r') as file:
            content = re.split('------------------------\n',file.read())
            origin, new = content[0].strip().split('\n'), content[1].strip().split('\n')
        if float(origin[0].split(',')[1]) % 0.5 == 0 and float(origin[-1].split(',')[1]) == 8.0:
            layout_info = [origin, new]
            all_layouts[name] = layout_info

    num = 0
    result = []
    # all_layouts's key: file name, value: [origin, new]
    for epoch in all_layouts.keys():
        num += 1
        print('File source:',epoch,'\n\tas',num,'of',len(all_layouts.keys()),'files')
        layout_info = all_layouts[epoch]
        origin, new, notes = init_layout(layout_info)

        '''
            Start implementing from here
            origin: 所有原曲旋律信息
                [
                    'note1_start_time,note1_end_time,note1_pitch',
                    'note2_start_time,note2_end_time,note2_pitch',
                    ...
                ]
            new: 所有magenta generated旋律信息
                [
                    'note1_start_time,note1_end_time,note1_pitch',
                    'note2_start_time,note2_end_time,note2_pitch',
                    ...
                ]
            notes: 所有旋律信息
                {
                    (note_start_time,note_end_time): #key
                        (
                            origin_note_pitch,
                            [new_note1_pitch,new_note2_pitch,...]
                        ),
                    ...
                }
        '''
        agent = qLearningAgent()
        sorted_notes = sorted(notes, key = lambda time: time[0])
        # import collections 
        # dic = collections.OrderedDict(sorted(notes.items(), key=lambda kv: kv[0], reverse=True))

        # print('notes:', notes)
        all_actions = []
        for i in range(agent.num_iter):
            # print(sorted_notes)
            # print(sorted_notes[1][1])
            count = 0
            # global global_actions = []
            init_state = state(sorted_notes[0][0], sorted_notes[0][1], notes[sorted_notes[0]][0], notes[sorted_notes[0]][1], notes,[])
            s = init_state
            while (1):
                # print(count)
                count +=1
                # agent.compute_value_from_qvalues(s)
                action = agent.get_action(s)
                next_s = s.get_next_state()

                if s == init_state:
                    agent.update(s, action, next_s, get_major_reward(s.root, action))
                else:
                    agent.update(s, action, next_s, get_total_reward(s.root, action, s.get_previous_state().root, s.actions[-1]))
                if s.is_end():
                    break
                s = next_s
            all_actions.append(s.actions)
        
        selected = ','.join([str(i) for i in all_actions[-1]])+'\n'
        line = ','.join([epoch,selected])
        result.append(line)
    print('Writing all selected pitches into files...')
    with open(out_file,'w') as file:
        file.writelines(result)
    print('Finished')
