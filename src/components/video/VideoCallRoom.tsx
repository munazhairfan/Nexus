import React, { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

export const VideoCallRoom: React.FC = () => {
  const { room_id } = useParams<{ room_id: string }>();
  const navigate = useNavigate();
  const [localStream, setLocalStream] = useState<MediaStream | null>(null);
  const [remoteStream, setRemoteStream] = useState<MediaStream | null>(null);
  const peerConnection = useRef<RTCPeerConnection | null>(null);
  const socket = useRef<WebSocket | null>(null);
  const localVideoRef = useRef<HTMLVideoElement>(null);
  const remoteVideoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const token = localStorage.getItem('business_nexus_token');
    if (!token) {
      navigate('/login');
      return;
    }

    const wsUrl = `ws://localhost:8001/api/v1/video/stream/${room_id}?token=${token}`;
    socket.current = new WebSocket(wsUrl);

    socket.current.onopen = () => {
      startMedia();
      socket.current?.send(JSON.stringify({ type: 'join' }));
    };

    socket.current.onmessage = async (event) => {
      const data = JSON.parse(event.data);
      if (!peerConnection.current) createPeerConnection();

      if (data.type === 'join') {
        const offer = await peerConnection.current!.createOffer();
        await peerConnection.current!.setLocalDescription(offer);
        socket.current?.send(JSON.stringify({ type: 'offer', sdp: offer }));
      } else if (data.type === 'offer') {
        await peerConnection.current!.setRemoteDescription(new RTCSessionDescription(data.sdp));
        const answer = await peerConnection.current!.createAnswer();
        await peerConnection.current!.setLocalDescription(answer);
        socket.current?.send(JSON.stringify({ type: 'answer', sdp: answer }));
      } else if (data.type === 'answer') {
        await peerConnection.current!.setRemoteDescription(new RTCSessionDescription(data.sdp));
      } else if (data.type === 'ice-candidate') {
        await peerConnection.current!.addIceCandidate(new RTCIceCandidate(data.candidate));
      }
    };

    socket.current.onclose = (event) => {
      if (event.code === 4001) toast.error('Room Full');
      else if (event.code === 4003) toast.error('Unauthorized');
      else toast.error('Call disconnected');
      navigate('/dashboard');
    };

    return () => {
      socket.current?.close();
      localStream?.getTracks().forEach(track => track.stop());
    };
  }, [room_id]);

  const startMedia = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    setLocalStream(stream);
    if (localVideoRef.current) localVideoRef.current.srcObject = stream;
    stream.getTracks().forEach(track => peerConnection.current?.addTrack(track, stream));
  };

  const createPeerConnection = () => {
    peerConnection.current = new RTCPeerConnection({ iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] });
    peerConnection.current.onicecandidate = (event) => {
      if (event.candidate) {
        socket.current?.send(JSON.stringify({ type: 'ice-candidate', candidate: event.candidate }));
      }
    };
    peerConnection.current.ontrack = (event) => {
      setRemoteStream(event.streams[0]);
      if (remoteVideoRef.current) remoteVideoRef.current.srcObject = event.streams[0];
    };
  };

  const toggleMedia = (type: 'audio' | 'video') => {
    localStream?.getTracks().forEach(track => {
      if (track.kind === type) {
        track.enabled = !track.enabled;
        socket.current?.send(JSON.stringify({ type: 'media-toggle', track: type, enabled: track.enabled }));
      }
    });
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-900 text-white">
      <div className="grid grid-cols-2 gap-4 w-full max-w-4xl">
        <video ref={localVideoRef} autoPlay playsInline muted className="bg-gray-800 rounded-lg" />
        <video ref={remoteVideoRef} autoPlay playsInline className="bg-gray-800 rounded-lg" />
      </div>
      <div className="flex gap-4 mt-6">
        <button onClick={() => toggleMedia('audio')} className="px-4 py-2 bg-blue-600 rounded">Mute Audio</button>
        <button onClick={() => toggleMedia('video')} className="px-4 py-2 bg-blue-600 rounded">Stop Video</button>
      </div>
    </div>
  );
};
