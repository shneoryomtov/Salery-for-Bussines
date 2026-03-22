import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'מחשבון הכנסה לעצמאים בישראל',
  description: 'כלי אישי להערכת הכנסות ותכנון כספי לעצמאים בישראל',
  
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="he" dir="rtl">
      <body className="bg-gray-50 text-gray-900">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 py-6">
            <h1 className="text-3xl font-bold text-blue-600">💰 מחשבון הכנסה לעצמאים</h1>
            <p className="text-gray-600 mt-2">כלי אישי להערכת הכנסות, הוצאות ומסים לעצמאים בישראל</p>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-4 py-8">
          {children}
        </main>
        <footer className="bg-gray-800 text-white mt-12 py-6">
          <div className="max-w-7xl mx-auto px-4 text-center">
            <p>© 2026 - כלי אישי להערכת הכנסות לעצמאים בישראל. לא תייעוץ מס רשמי.</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
