"use client";

import { useState, useEffect } from "react";
import Header from "@/components/Header";

interface User {
  id: number;
  username: string;
  display_name: string;
  role: string;
}

export default function AdminHelpPage() {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        window.location.href = "/auth/login";
        return;
      }

      const res = await fetch("http://localhost:8000/auth/me", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) {
        localStorage.removeItem("token");
        window.location.href = "/auth/login";
        return;
      }

      const userData = await res.json();
      if (userData.role !== "admin") {
        window.location.href = "/";
        return;
      }

      setUser(userData);
    } catch (err) {
      console.error("Auth check failed:", err);
      window.location.href = "/auth/login";
    }
  };

  if (!user || user.role !== "admin") {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-xl text-gray-600 mb-4">กำลังตรวจสอบสิทธิ์...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />

      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            คู่มือใช้งานบนเครื่อง
          </h1>
          <p className="text-gray-600 mt-2">
            คำแนะนำในการติดตั้ง ตั้งค่า และใช้งาน Thai ID Team OCR
          </p>
        </div>

        <div className="space-y-8">
          {/* Getting Started */}
          <Section title="🚀 เริ่มต้นใช้งาน">
            <Subsection title="1. เริ่ม Backend API Server">
              <CodeBlock>
{`cd apps/api
python -m venv venv
source venv/bin/activate  # หรือ venv\\Scripts\\activate (Windows)
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`}
              </CodeBlock>
              <p>Backend จะใช้ port 8000</p>
            </Subsection>

            <Subsection title="2. เริ่ม Frontend Web Server">
              <CodeBlock>
{`cd apps/web
npm install
npm run dev`}
              </CodeBlock>
              <p>Frontend จะใช้ port 3000 ที่ http://localhost:3000</p>
            </Subsection>

            <Subsection title="3. สร้าง Admin User">
              <p>เข้าไปที่ http://localhost:3000/auth/bootstrap-admin</p>
              <p>สร้าง admin user คนแรก (ทำได้แค่ครั้งเดียว)</p>
            </Subsection>
          </Section>

          {/* Core Features */}
          <Section title="📋 ฟีเจอร์หลัก">
            <Subsection title="การสร้างทีม (Teams)">
              <ul className="list-disc list-inside space-y-1">
                <li>ไปที่หน้า Teams</li>
                <li>กดปุ่ม "Create Team"</li>
                <li>ใส่ชื่อทีม หมวดอายุ เพศ</li>
                <li>กดปุ่ม "Create"</li>
              </ul>
            </Subsection>

            <Subsection title="อัปโหลดและ OCR (Upload & OCR)">
              <ul className="list-disc list-inside space-y-1">
                <li>ไปที่หน้า OCR</li>
                <li>เลือกทีม</li>
                <li>อัปโหลดรูปบัตรประชาชน หรือเอกสารแอปพลิเคชัน</li>
                <li>ระบบจะ OCR และแสดงชื่อที่สกัด</li>
                <li>ตรวจสอบและแก้ไขชื่อถ้าจำเป็น</li>
              </ul>
            </Subsection>

            <Subsection title="ตรวจสอบและยืนยัน (Review)">
              <ul className="list-disc list-inside space-y-1">
                <li>ไปที่หน้า Review</li>
                <li>ตรวจสอบชื่อที่สกัดได้</li>
                <li>กด Verify เพื่อยืนยัน หรือแก้ไข</li>
                <li>สามารถเพิ่มวันเกิด และข้อมูลอื่นได้</li>
              </ul>
            </Subsection>

            <Subsection title="ส่งออกไฟล์ Excel (Export)">
              <ul className="list-disc list-inside space-y-1">
                <li>ไปที่หน้า Export</li>
                <li>เลือกทีม</li>
                <li>กดปุ่ม "Export to XLSX"</li>
                <li>ไฟล์ Excel จะดาวน์โหลดมา</li>
              </ul>
            </Subsection>
          </Section>

          {/* Admin Features */}
          <Section title="👨‍💼 ฟีเจอร์ Admin">
            <Subsection title="สถานะระบบ (System Health)">
              <ul className="list-disc list-inside space-y-1">
                <li>ตรวจสอบสถานะฐานข้อมูล</li>
                <li>ตรวจสอบ Tesseract OCR</li>
                <li>ตรวจสอบ Thai Language Data</li>
                <li>ตรวจสอบ Poppler สำหรับ PDF</li>
                <li>ดูสถิติจำนวนทีม ผู้เล่น บันทึก</li>
                <li>ดูการใช้พื้นที่ storage</li>
              </ul>
            </Subsection>

            <Subsection title="สำรองและฟื้นฟูข้อมูล (Backup/Restore)">
              <ul className="list-disc list-inside space-y-1">
                <li>สร้างไฟล์สำรองฐานข้อมูล</li>
                <li>เลือกว่าจะรวมไฟล์ Export หรือไม่</li>
                <li>ดาวน์โหลดไฟล์สำรอง</li>
                <li>
                  ฟื้นฟูข้อมูล (ต้องพิมพ์ RESTORE_CONFIRM เพื่อยืนยัน)
                </li>
                <li>ลบไฟล์สำรองเก่า</li>
              </ul>
            </Subsection>
          </Section>

          {/* Installation & Setup */}
          <Section title="🔧 การติดตั้งส่วนประกอบ">
            <Subsection title="ติดตั้ง Tesseract OCR">
              <p className="font-medium mb-2">Windows:</p>
              <CodeBlock>
{`ดาวน์โหลด: https://github.com/UB-Mannheim/tesseract/wiki
รัน installer แล้วจำ path ของ Tesseract`}
              </CodeBlock>

              <p className="font-medium mb-2 mt-4">macOS:</p>
              <CodeBlock>{`brew install tesseract`}</CodeBlock>

              <p className="font-medium mb-2 mt-4">Linux (Ubuntu/Debian):</p>
              <CodeBlock>{`sudo apt-get install tesseract-ocr`}</CodeBlock>
            </Subsection>

            <Subsection title="ติดตั้ง Thai Language Data">
              <p>Thai language data จะดาวน์โหลดโดยอัตโนมัติ</p>
              <p>หรือดาวน์โหลดแบบ manual:</p>
              <CodeBlock>
{`# บน Windows
https://github.com/UB-Mannheim/tesseract/wiki
- เลือก "Additional language data"
- ดาวน์โหลด tha.traineddata

# บน Linux/macOS
sudo apt-get install tesseract-ocr-tha  # Ubuntu/Debian
brew install tesseract-lang  # macOS`}
              </CodeBlock>
            </Subsection>

            <Subsection title="ติดตั้ง Poppler (สำหรับ PDF)">
              <p className="font-medium mb-2">Windows:</p>
              <CodeBlock>
{`https://github.com/oschwartz10612/poppler-windows/releases/
ดาวน์โหลด release ล่าสุด และแตกไฟล์`}
              </CodeBlock>

              <p className="font-medium mb-2 mt-4">macOS:</p>
              <CodeBlock>{`brew install poppler`}</CodeBlock>

              <p className="font-medium mb-2 mt-4">Linux:</p>
              <CodeBlock>{`sudo apt-get install poppler-utils`}</CodeBlock>
            </Subsection>
          </Section>

          {/* Backup & Restore */}
          <Section title="💾 สำรองและฟื้นฟูข้อมูล">
            <Subsection title="สร้าง Backup">
              <ol className="list-decimal list-inside space-y-2">
                <li>เข้าไปที่ Admin → สำรองข้อมูล</li>
                <li>เลือก "รวมไฟล์ Export" ถ้าต้องการ</li>
                <li>กดปุ่ม "สร้างไฟล์สำรอง"</li>
                <li>ไฟล์ zip จะสร้างขึ้นใน backups/ folder</li>
              </ol>
            </Subsection>

            <Subsection title="ฟื้นฟูข้อมูล">
              <ol className="list-decimal list-inside space-y-2">
                <li>เข้าไปที่ Admin → สำรองข้อมูล</li>
                <li>เลือกไฟล์ที่ต้องการ</li>
                <li>กดปุ่ม "ฟื้นฟู"</li>
                <li>พิมพ์ "RESTORE_CONFIRM" เพื่อยืนยัน</li>
                <li>กดปุ่ม "ฟื้นฟู" อีกครั้ง</li>
                <li>
                  รอจนเสร็จ แล้ว Restart Backend API Server
                </li>
              </ol>
            </Subsection>
          </Section>

          {/* Privacy & Security */}
          <Section title="🔒 ความเป็นส่วนตัวและความปลอดภัย">
            <Subsection title="Checklist:">
              <ul className="list-disc list-inside space-y-1">
                <li>
                  ✅ ไม่เก็บเลขบัตรประชาชน (13 หลัก)
                </li>
                <li>
                  ✅ ไม่ส่งรูปบัตรไปยัง Cloud API
                </li>
                <li>✅ OCR ทำบนเครื่องเท่านั้น</li>
                <li>
                  ✅ ฐานข้อมูลเป็น SQLite บนเครื่องท้องถิ่น
                </li>
                <li>
                  ✅ ไฟล์สำรองจำกัดสิทธิ์ (Admin only)
                </li>
                <li>
                  ✅ ยืนยันตัวตนก่อน Restore ข้อมูล
                </li>
                <li>
                  ✅ บันทึก audit log ทุกการกระทำ
                </li>
                <li>
                  ✅ ลบข้อมูลเก่าที่ไม่ต้องการได้
                </li>
              </ul>
            </Subsection>
          </Section>

          {/* Troubleshooting */}
          <Section title="🔧 แก้ไขปัญหา">
            <Subsection title="Tesseract not found">
              <p>
                ติดตั้ง Tesseract และตรวจสอบว่าอยู่ใน PATH
              </p>
            </Subsection>

            <Subsection title="Thai language data missing">
              <p>ติดตั้ง tesseract-ocr-tha package</p>
            </Subsection>

            <Subsection title="Poppler not found">
              <p>
                ติดตั้ง Poppler สำหรับสนับสนุน PDF
                (ไม่จำเป็นถ้ากำลังใช้รูป)
              </p>
            </Subsection>

            <Subsection title="Backend not responding">
              <ul className="list-disc list-inside space-y-1">
                <li>ตรวจสอบว่า Backend ทำงาน</li>
                <li>ตรวจสอบ port 8000</li>
                <li>ดู error logs บน Terminal</li>
              </ul>
            </Subsection>
          </Section>

          {/* Support */}
          <Section title="❓ ความช่วยเหลือเพิ่มเติม">
            <p>
              หากต้องการความช่วยเหลือเพิ่มเติม ติดต่อ admin หรือตรวจสอบ
              README.md ในโฟลเดอร์โปรเจกต์
            </p>
          </Section>
        </div>
      </div>
    </div>
  );
}

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">{title}</h2>
      <div className="space-y-4">{children}</div>
    </div>
  );
}

function Subsection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <h3 className="text-lg font-semibold text-gray-900 mb-3">{title}</h3>
      <div className="space-y-2 text-gray-700">{children}</div>
    </div>
  );
}

function CodeBlock({ children }: { children: string }) {
  return (
    <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
      <code>{children}</code>
    </pre>
  );
}
