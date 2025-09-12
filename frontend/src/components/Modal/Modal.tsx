import { useEffect, useState } from "react";
import { createPortal } from "react-dom";

interface ModalProps {
  children: React.ReactNode;
  onClose?: () => void;
}

const Modal: React.FC<ModalProps> = ({ children, onClose }) => {
  const [mounted, setMounted] = useState(false);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    setMounted(true);
    setTimeout(() => setVisible(true), 10); // trigger enter animation
  }, []);

  const handleClose = () => {
    setVisible(false);
    setTimeout(() => {
      if (onClose) onClose();
    }, 250); // matches animation duration
  };

  if (!mounted) return null;

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className={`absolute inset-0 bg-black/50 backdrop-blur-sm transition-opacity duration-300 ${
          visible ? "opacity-100" : "opacity-0"
        }`}
        onClick={handleClose}
      />

      {/* Modal content */}
      <div className="relative z-10 w-full max-w-md px-4">
        <div
          className={`transform transition-all duration-300 ${
            visible ? "animate-modal-enter" : "animate-modal-exit"
          }`}
        >
          {children}
        </div>
      </div>
    </div>,
    document.body
  );
};

export default Modal;