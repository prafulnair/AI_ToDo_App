// src/components/ToastProvider.tsx
import { ToastContainer, useToast } from '@rewind-ui/core';
import { createContext, useContext } from 'react';

const ToastContext = createContext<any>(null);

export const ToastProvider = ({ children }: { children: React.ReactNode }) => {
  const toast = useToast();

  const notify = {
    success: (msg: string) =>
      toast.add({
        title: 'Task added Successfully',
        description: msg,
        variant: 'success',
        iconType: 'success',
        shadow: 'lg',
        radius: 'md',
      }),
    danger: (msg: string) =>
      toast.add({
        title: 'Deleted',
        description: msg,
        variant: 'danger',
        iconType: 'error',
        shadow: 'lg',
        radius: 'md',
      }),
    info: (msg: string) =>
      toast.add({
        title: 'Info',
        description: msg,
        variant: 'info',
        iconType: 'info',
        shadow: 'lg',
        radius: 'md',
      }),
    warning: (msg: string) =>
      toast.add({
        title: 'Warning',
        description: msg,
        variant: 'warning',
        iconType: 'warning',
        shadow: 'lg',
        radius: 'md',
      }),
  };

  return (
    <ToastContext.Provider value={notify}>
      {children}
      <ToastContainer position="top-right" max={4} />
    </ToastContext.Provider>
  );
};

export const useNotify = () => useContext(ToastContext);