import React, { useState } from 'react';
import { X } from 'lucide-react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import apiClient from '../../api/client';
import toast from 'react-hot-toast';

interface ScheduleMeetingModalProps {
  isOpen: boolean;
  onClose: () => void;
  inviteeId: string;
  onSuccess?: () => void;
}

export const ScheduleMeetingModal: React.FC<ScheduleMeetingModalProps> = ({
  isOpen,
  onClose,
  inviteeId,
  onSuccess
}) => {
  const [title, setTitle] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        title,
        invitee_id: inviteeId,
        start_time: new Date(startTime).toISOString(),
        end_time: new Date(endTime).toISOString()
      };
      await apiClient.post('/meetings/', payload);
      toast.success('Meeting scheduled!');
      if (onSuccess) onSuccess();
      onClose();
    } catch (error: any) {
      if (error.response?.status === 400) {
        toast.error('Scheduling conflict detected. One or more participants are already booked during this time slot.');
      } else {
        toast.error('Failed to schedule meeting');
      }
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-bold">Schedule Meeting</h2>
          <button onClick={onClose}><X size={20} /></button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Meeting Title" value={title} onChange={(e) => setTitle(e.target.value)} required />
          <Input label="Start Time" type="datetime-local" value={startTime} onChange={(e) => setStartTime(e.target.value)} required />
          <Input label="End Time" type="datetime-local" value={endTime} onChange={(e) => setEndTime(e.target.value)} required />
          <div className="flex justify-end space-x-2">
            <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
            <Button type="submit">Schedule</Button>
          </div>
        </form>
      </div>
    </div>
  );
};
