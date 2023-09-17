import cv2
from pyzbar.pyzbar import decode

def detect_qr_code():
    # Initialize the camera
    cap = cv2.VideoCapture(0)
    
    # Variable to keep track of detected QR codes
    detected_qr_codes = set()
    
    while True:
        # Read frame from the camera
        ret, frame = cap.read()
        
        # Detect QR codes in the frame
        decoded_objects = decode(frame)
        
        # Process each detected QR code
        for obj in decoded_objects:
            # Extract QR code data as string
            qr_data = obj.data.decode('utf-8')
            
            # Check if QR code has been detected before
            if qr_data not in detected_qr_codes:
                # Add the QR code to the set of detected codes
                detected_qr_codes.add(qr_data)
                
                # Print the QR code data
                print("QR Code Detected: ", qr_data)
        
        # Display the frame
        cv2.imshow("QR Code Detection", frame)
        
        # Check for 'q' key press to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release the camera and close windows
    cap.release()
    cv2.destroyAllWindows()

# Call the function to start QR code detection
detect_qr_code()