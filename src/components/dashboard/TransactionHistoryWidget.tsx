import React, { useEffect, useState } from 'react';
import { Card, CardBody, CardHeader } from '../ui/Card';
import apiClient from '../../api/client';

export const TransactionHistoryWidget: React.FC = () => {
  const [transactions, setTransactions] = useState<any[]>([]);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await apiClient.get('/payments/history');
      setTransactions(res.data);
    } catch (error) {
      console.error('Failed to fetch transaction history');
    }
  };

  return (
    <Card>
      <CardHeader>
        <h2 className="text-lg font-medium text-gray-900">Transaction History</h2>
      </CardHeader>
      <CardBody className="space-y-4">
        {transactions.map((t) => (
          <div key={t._id} className="flex justify-between border-b pb-2">
            <div>
              <p className="font-medium capitalize">{t.transaction_type}</p>
              <p className="text-sm text-gray-500">{new Date(t.created_at).toLocaleString()}</p>
            </div>
            <div className="text-right">
              <p className={`font-semibold ${t.status === 'Failed' ? 'text-red-600' : 'text-gray-900'}`}>
                {t.transaction_type === 'withdraw' ? '-' : '+'}${t.amount.toFixed(2)}
              </p>
              <p className="text-sm text-gray-500">{t.status}</p>
            </div>
          </div>
        ))}
      </CardBody>
    </Card>
  );
};
