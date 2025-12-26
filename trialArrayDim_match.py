from deepface import DeepFace
import shutil
import os

input_dir = 'c:\\Users\\hamid\\pyCode\\uploads\\'
output_dir = 'c:\\Users\\hamid\\pyCode\\SortedImages\\'
i = 0
#for fname in os.listdir(input_dir):
while True:
    f = os.listdir(input_dir)
    dir_path = os.path.join(output_dir, str(i))
    os.makedirs(dir_path)
    fname = f.pop()

    if fname.endswith(('.jpg','.jpeg','.png')):
        loc_image_path = os.path.join(input_dir, fname)
        dfs = DeepFace.find(img_path=loc_image_path, db_path= 'C:\\Users\\hamid\\pyCode\\uploads', 
            detector_backend = "yunet",enforce_detection=False)

    
        for it in dfs[0]:
            print(it) 
        
        print(len(dfs[0]['identity']))
        cnt = 0
        for it in dfs[0]['identity']:
            filename = it.split('\\')
            lastInd = len(filename) - 1
            (identity, target_x, target_y, target_w, target_h, source_x, source_y, source_w, source_y, threshold, distance) = (
                dfs[0]['identity'][cnt],
                dfs[0]['target_x'][cnt],
                dfs[0]['target_y'][cnt],
                dfs[0]['target_w'][cnt],
                dfs[0]['target_h'][cnt],
                dfs[0]['target_x'][cnt],
                dfs[0]['target_x'][cnt],
                dfs[0]['target_w'][cnt],
                dfs[0]['target_h'][cnt],
                dfs[0]['threshold'][cnt],
                dfs[0]['distance'][cnt])
            #print("target_x= %d, target_y=%d, target_w=%d, target_h=%d, source_x=%d, source_y=%d, source_w=%d, source_y=%d, threshold=%.5f, distance=%.5f"%(identity, target_x, target_y, target_w, target_h, source_x, source_y, source_w, source_y, str(threshold), str(distance)))
            print("Image: ", filename[lastInd], " distance = ", dfs[0]['distance'][cnt])
            if distance < 0.35:
                print("Copying %s to %s"%(it,  os.path.join(dir_path,filename[lastInd])))
                shutil.move(it, os.path.join(dir_path,filename[lastInd]))
                #shutil.move(loc_image_path, dir_path)
                #break;
            cnt = cnt + 1
        cnt = 0
    i = i + 1




'''
dfs = DeepFace.find(
    img_path='C:\\Users\\hamid\\pyCode\\uploads\\Face_21_38_53_cnt_155_.jpg',
    db_path= 'C:\\Users\\hamid\\pyCode\\uploads',
    detector_backend = "yunet",
)
'''
for it in dfs[0]['identity']:
    print(it)


print(dfs)