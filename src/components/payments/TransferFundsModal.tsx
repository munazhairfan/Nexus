import React, { useState } from 'react';
import { X } from 'lucide-react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import apiClient from '../../api/client';
import toast from 'react-hot-toast';

interface TransferFundsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const TransferFundsModal: React.FC<TransferFundsModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [recipientId, setRecipientId] = useState('');
  const [amount, setAmount] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await apiClient.post('/payments/transfer', {
        recipient_id: recipientId,
        amount: parseFloat(amount)
      });
      
      if (response.data.status === 'Failed') {
        toast.error('Transaction Failed: Simulated platform clearing fault.');
      } else {
        toast.success('Transfer completed successfully!');
      }
      onSuccess();
      onClose();
    } catch (error: any) {
      toast.error('Failed to process transfer');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-bold">Transfer Funds</h2>
          <button onClick={onClose}><X size={20} /></button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Recipient ID" value={recipientId} onChange={(e) => setRecipientId(e.target.value)} required />
          <Input label="Amount (USD)" type="number" step="0.01" value={amount} onChange={(e) => setAmount(e.target.value)} required />
          <Button type="submit" disabled={loading}>{loading ? 'Processing...' : 'Transfer'}</Button>
        </form>
      </div>
    </div>
  );
};
