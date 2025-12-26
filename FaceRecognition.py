import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, BatchNormalization
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import pickle
import mediapipe as mp
import matplotlib.pyplot as plt

# Constants
DATASET_PATH = "C:\\Users\\hamid\\pyCode\\FR\\Humans"  # training data path
MODEL_PATH = "C:/Users/hamid/pyCode/FR/model/face_recognition_model.h5"  # Saved model
ENCODER_PATH = "C:/Users/hamid/pyCode/FR/LabelData/label_encoder.pkl"  # Saved label encoder
IMG_SIZE = (224, 224)  # Image input size for EfficientNetB0

# Load images and labels from dataset
def load_images_from_directory(directory):
    images, labels = [], []
    for class_name in os.listdir(directory):
        class_dir = os.path.join(directory, class_name)
        if not os.path.isdir(class_dir):
            continue
        for image_name in os.listdir(class_dir):
            if image_name.endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(class_dir, image_name)
                try:
                    img = cv2.imread(image_path)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img = cv2.resize(img, IMG_SIZE)
                    images.append(img)
                    labels.append(class_name)
                except Exception as e:
                    print(f"Error processing {image_path}: {e}")
    return np.array(images), np.array(labels)

# Create a binary classification model
def create_model():
    base_model = EfficientNetB0(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = BatchNormalization()(x)
    x = Dense(256, activation='relu')(x)
    #x = Dropout(0.5)(x)
    predictions = Dense(1, activation='sigmoid')(x)  # Binary classification
    model = Model(inputs=base_model.input, outputs=predictions)

    # Freeze base layers initially
    for layer in base_model.layers:
        layer.trainable = False

    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
    return model


def train_model():
    print("Loading dataset...")
    images, labels = load_images_from_directory(DATASET_PATH)
    print(f"Loaded {len(images)} images.")

    if len(images) < 100:
        print("Insufficient data. Please add more images (200+ per class recommended).")
        return

    # Encode labels
    label_encoder = LabelEncoder()
    labels = label_encoder.fit_transform(labels)

    # Save the label encoder
    with open(ENCODER_PATH, 'wb') as f:
        pickle.dump(label_encoder, f)

    # Normalize images
    images = images / 255.0

    # Split dataset
    X_train, X_val, y_train, y_val = train_test_split(images, labels, test_size=0.2, random_state=42, shuffle=True)

    # Enhanced Data Augmentation
    datagen = ImageDataGenerator(
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.3,
        brightness_range=[0.8, 1.2],
        horizontal_flip=True,
        fill_mode='nearest'
    )

    # Generators for training and validation
    train_generator = datagen.flow(X_train, y_train, batch_size=16)
    val_generator = ImageDataGenerator().flow(X_val, y_val, batch_size=16)

    # Create the model
    model = create_model()

    # Disable EarlyStopping during initial training
    callbacks = [
        tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5)
    ]

    print("Training classifier head...")
    history = model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=20,  # Allow up to 20 epochs
        steps_per_epoch=len(X_train) // 16,
        validation_steps=len(X_val) // 16,
        callbacks=callbacks
    )

    print("Fine-tuning the model...")
    for layer in model.layers:
        layer.trainable = True  # Unfreeze all layers

    # Re-enable EarlyStopping during fine-tuning
    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5)
    ]

    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=5e-6),
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    history_fine = model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=20,  # Allow up to 20 epochs for fine-tuning
        steps_per_epoch=len(X_train) // 16,
        validation_steps=len(X_val) // 16,
        callbacks=callbacks
    )


    # Save the model
    model.save(MODEL_PATH)
    print(f"Model saved at {MODEL_PATH}")

    # Plot training history
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Train Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.plot(history_fine.history['accuracy'], label='Fine-tuned Train Accuracy')
    plt.plot(history_fine.history['val_accuracy'], label='Fine-tuned Validation Accuracy')
    plt.legend()
    plt.title('Accuracy')

    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.plot(history_fine.history['loss'], label='Fine-tuned Train Loss')
    plt.plot(history_fine.history['val_loss'], label='Fine-tuned Validation Loss')
    plt.legend()
    plt.title('Loss')
    plt.show()

# Real-time face recognition
def live_face_recognition():
    print("Loading model and encoder...")
    model = tf.keras.models.load_model(MODEL_PATH)
    with open(ENCODER_PATH, 'rb') as f:
        label_encoder = pickle.load(f)
    class_names = label_encoder.classes_

    mp_face_detection = mp.solutions.face_detection
    cap = cv2.VideoCapture(0)  # Start webcam

    with mp_face_detection.FaceDetection(min_detection_confidence=0.7) as face_detection:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame. Exiting...")
                break

            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_detection.process(img_rgb)

            if results.detections:
                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    h, w, _ = frame.shape
                    x = max(0, int(bbox.xmin * w))
                    y = max(0, int(bbox.ymin * h))
                    w_box = int(bbox.width * w)
                    h_box = int(bbox.height * h)
                    x_end = min(w, x + w_box)
                    y_end = min(h, y + h_box)

                    face_img = img_rgb[y:y_end, x:x_end]
                    if face_img.size == 0:
                        continue

                    face_img = cv2.resize(face_img, IMG_SIZE)
                    face_img_ed = np.expand_dims(face_img, axis=0) / 255.0
                    #face_img_un = np.expand_dims(face_img, axis=0)

                    predictions_ed = model.predict(face_img_ed)

                    #predictions_un = model.predict(face_img_un)
                    predictions_ed = model.predict(face_img_ed)

                    #confidence_un = predictions_un[0][0]
                    confidence_ed = predictions_ed[0][0]
                    label = "YourFace" if confidence_ed > 0.8 else "NotYourFace"  # Increased threshold
                    

                    color = (0, 255, 0) if label == "YourFace" else (0, 0, 255)
                    text = f"{label} ({confidence_ed:.2f})"
                    cv2.rectangle(frame, (x, y), (x_end, y_end), color, 2)
                    cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            cv2.imshow("Live Face Recognition", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Exiting...")
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    print("1: Train the model")
    print("2: Run live face recognition")
    choice = input("Choose an option: ")
    if choice == "1":
        train_model()
    elif choice == "2":
        live_face_recognition()