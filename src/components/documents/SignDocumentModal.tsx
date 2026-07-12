import React, { useRef } from 'react';
import { X } from 'lucide-react';
import { Button } from '../ui/Button';
import apiClient from '../../api/client';
import toast from 'react-hot-toast';

interface SignDocumentModalProps {
  isOpen: boolean;
  onClose: () => void;
  documentId: string;
  onSuccess: () => void;
}

export const SignDocumentModal: React.FC<SignDocumentModalProps> = ({ isOpen, onClose, documentId, onSuccess }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  if (!isOpen) return null;

  const handleSign = async () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const signature_base64 = canvas.toDataURL('image/png');
    
    try {
      await apiClient.post(`/documents/${documentId}/sign`, { signature_base64 });
      toast.success('Signature appended successfully');
      onSuccess();
      onClose();
    } catch (error) {
      toast.error('Failed to sign document');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-bold">Sign Document</h2>
          <button onClick={onClose}><X size={20} /></button>
        </div>
        <canvas ref={canvasRef} className="border w-full h-40 mb-4 bg-gray-50" />
        <div className="flex justify-end space-x-2">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={handleSign}>Sign</Button>
        </div>
      </div>
    </div>
  );
};
