#!/usr/bin/env python3
import tkinter
import matplotlib
matplotlib.use('TkAgg')

from HandTrackerRenderer import HandTrackerRenderer, LINES_HAND
import argparse
import numpy as np
import matplotlib.pyplot as plt

effectors = [point for (point,_) in LINES_HAND]
end_effector_idx = []
for line in LINES_HAND:
    if not line[1] in effectors:
        end_effector_idx.append(line[1])

parser = argparse.ArgumentParser()
parser.add_argument('-e', '--edge', action="store_true",
                    help="Use Edge mode (postprocessing runs on the device)")
parser_tracker = parser.add_argument_group("Tracker arguments")
parser_tracker.add_argument('-i', '--input', type=str, 
                    help="Path to video or image file to use as input (if not specified, use OAK color camera)")
parser_tracker.add_argument("--pd_model", type=str,
                    help="Path to a blob file for palm detection model")
parser_tracker.add_argument('--no_lm', action="store_true", 
                    help="Only the palm detection model is run (no hand landmark model)")
parser_tracker.add_argument("--lm_model", type=str,
                    help="Landmark model 'full', 'lite', 'sparse' or path to a blob file")
parser_tracker.add_argument('--use_world_landmarks', action="store_true", 
                    help="Fetch landmark 3D coordinates in meter")                  
parser_tracker.add_argument('-xyz', "--xyz", action="store_true", 
                    help="Enable spatial location measure of palm centers")
parser_tracker.add_argument('-g', '--gesture', action="store_true", 
                    help="Enable gesture recognition")
parser_tracker.add_argument('-c', '--crop', action="store_true", 
                    help="Center crop frames to a square shape")
parser_tracker.add_argument('-f', '--internal_fps', type=int, 
                    help="Fps of internal color camera. Too high value lower NN fps (default= depends on the model)")                    
parser_tracker.add_argument("-r", "--resolution", choices=['full', 'ultra'], default='full',
                    help="Sensor resolution: 'full' (1920x1080) or 'ultra' (3840x2160) (default=%(default)s)")
parser_tracker.add_argument('--internal_frame_height', type=int,                                                                                 
                    help="Internal color camera frame height in pixels")   
parser_tracker.add_argument("-lh", "--use_last_handedness", action="store_true",
                    help="Use last inferred handedness. Otherwise use handedness average (more robust)")                            
parser_tracker.add_argument('--single_hand_tolerance_thresh', type=int, default=10,
                    help="(Duo mode only) Number of frames after only one hand is detected before calling palm detection (default=%(default)s)")
parser_tracker.add_argument('--dont_force_same_image', action="store_true",
                    help="(Edge Duo mode only) Don't force the use the same image when inferring the landmarks of the 2 hands (slower but skeleton less shifted)")
parser_tracker.add_argument('-lmt', '--lm_nb_threads', type=int, choices=[1,2], default=2, 
                    help="Number of the landmark model inference threads (default=%(default)i)")  
parser_tracker.add_argument('-t', '--trace', type=int, nargs="?", const=1, default=0, 
                    help="Print some debug infos. The type of info depends on the optional argument.")                
parser_renderer = parser.add_argument_group("Renderer arguments")
parser_renderer.add_argument('-o', '--output', 
                    help="Path to output video file")
args = parser.parse_args()
dargs = vars(args)
tracker_args = {a:dargs[a] for a in ['pd_model', 'lm_model', 'internal_fps', 'internal_frame_height'] if dargs[a] is not None}

from HandTrackerEdge import HandTracker
tracker_args['use_same_image'] = not args.dont_force_same_image

tracker = HandTracker(
        input_src=args.input, 
        use_lm= not args.no_lm, 
        use_world_landmarks=True,
        use_gesture=args.gesture,
        xyz=False,
        solo=True,
        crop=args.crop,
        resolution=args.resolution,
        stats=True,
        trace=0,
        use_handedness_average=not args.use_last_handedness,
        single_hand_tolerance_thresh=args.single_hand_tolerance_thresh,
        lm_nb_threads=args.lm_nb_threads,
        **tracker_args
        )

renderer = HandTrackerRenderer(
        tracker=tracker,
        output=args.output)


import time
t = time.time()

def rotateY(point, theta):
    R = np.array([[ np.cos(theta), 0, np.sin(theta)],
                  [ 0,             1,             0],
                  [-np.sin(theta), 0, np.cos(theta)]])
    R @ point

def rotateZ(point, theta):
    R = np.array([[ np.cos(theta), np.sin(theta), 0],
                  [-np.sin(theta), np.cos(theta), 0],
                  [ 0,             0,             1],])
    R @ point

while True:
    # Run hand tracker on next frame
    # 'bag' contains some information related to the frame 
    # and not related to a particular hand like body keypoints in Body Pre Focusing mode
    # Currently 'bag' contains meaningful information only when Body Pre Focusing is used
    frame, hands, bag = tracker.next_frame()

    if frame is None: break

    if len(hands) > 0:
        t = time.time()
        print(f"Hands Detected: {len(hands)}")
        print(f"Number of Landmarks: {[len(hand.landmarks) for hand in hands]}")
        hand = hands[0]
        print(hand.world_landmarks)
        ax = plt.figure().add_subplot(projection='3d')
        for line in LINES_HAND:
            x = [hand.world_landmarks[p,0] for p in line]
            y = [-hand.world_landmarks[p,1] for p in line]
            z = [-hand.world_landmarks[p,2] for p in line]
            ax.plot(x, y, z)
            
        ax.scatter(hand.world_landmarks[:,0], -hand.world_landmarks[:,1], -hand.world_landmarks[:,2])
        ax.plot([0,0.1],[0,0],[0.1,0.1],'b')
        ax.plot([0,0],[0,0.1],[0.1,0.1],'g')
        ax.plot([0,0],[0,0],[0.1,0],'r')
        ax.set_xlabel('x [m]')
        ax.view_init(elev=90, azim=-90)
        plt.show()


        key_points = np.array([hand.world_landmarks[:,0], -hand.world_landmarks[:,1], -hand.world_landmarks[:,2]])
        end_effectors = key_points[:,end_effector_idx]
        exit(0)
        # def cost_func(x):

        #     starfish_ee = [rotateZ(rotateY([1,0,0], x[i]), 2*np.pi*i/5) for i in range(5)]
        #     # for h_ee in end_effectos:
        #     #     for s_ee in starfish_ee:
        #     #         if np.norm()

        #             # starfish_ee_matching = 
        #     return np.sum(end_effectors - starfish_ee)


        # while 1:
        #     pass

    # # Draw hands
    # frame = renderer.draw(frame, hands, bag)
    # key = renderer.waitKey(delay=1)
    # if key == 27 or key == ord('q'):
    #     break

# renderer.exit()
tracker.exit()
