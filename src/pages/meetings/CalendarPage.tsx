import React, { useState, useEffect } from 'react';
import { Card, CardBody, CardHeader } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import apiClient from '../../api/client';
import toast from 'react-hot-toast';

export const CalendarPage: React.FC = () => {
  const [meetings, setMeetings] = useState<any[]>([]);
  
  useEffect(() => {
    fetchMeetings();
  }, []);
  
  const fetchMeetings = async () => {
    try {
      const res = await apiClient.get('/meetings/my-calendar');
      setMeetings(res.data);
    } catch (error) {
      toast.error('Failed to load calendar');
    }
  };
  
  const handleStatusUpdate = async (meetingId: string, status: 'accepted' | 'rejected') => {
    try {
      await apiClient.patch(`/meetings/${meetingId}/status`, { status });
      toast.success(`Meeting ${status}`);
      fetchMeetings();
    } catch (error) {
      toast.error('Failed to update status');
    }
  };
  
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">My Calendar</h1>
      <Card>
        <CardBody className="space-y-4">
          {meetings.map((m) => (
            <div key={m._id} className="flex justify-between items-center border-b p-2">
              <div>
                <p className="font-semibold">{m.title}</p>
                <p className="text-sm text-gray-500">
                  {new Date(m.start_time).toLocaleString()} - {new Date(m.end_time).toLocaleTimeString()}
                </p>
                <p className="text-sm">With: {m.participant_profile.name}</p>
              </div>
              <div className="space-x-2">
                {m.status === 'pending' && (
                  <>
                    <Button variant="outline" size="sm" onClick={() => handleStatusUpdate(m._id, 'rejected')}>Decline</Button>
                    <Button size="sm" onClick={() => handleStatusUpdate(m._id, 'accepted')}>Accept</Button>
                  </>
                )}
                <Badge variant={m.status === 'accepted' ? 'success' : m.status === 'pending' ? 'warning' : 'gray'}>{m.status}</Badge>
              </div>
            </div>
          ))}
        </CardBody>
      </Card>
    </div>
  );
};
