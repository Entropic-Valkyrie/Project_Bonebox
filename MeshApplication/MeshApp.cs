using System;
using System.ComponentModel;
using System.IO.MemoryMappedFiles;
using System.Xml;

class Program
{
    static void Main()
    {
        using (var mmf = MemoryMappedFile.OpenExisting("pose_basic"))
        using (var accessor = mmf.CreateViewAccessor())
        {
            int Calcheck = 0;
            int Calibration = 0;
            float XSum = 0;
            float YSum = 0;
            float ZSum = 0;
            float[] coords = new float(128);
            float[] CalCord = new float(128);
            static float VChange (float a, float b)
            {
                    return Math.Abs((a + b));
            }
            static float AveCalk (float[] a, char b)
            {
                int n = 0;
                float tempx = 0;
                if (b = 'x'){while (n <= 32)
                    {
                        tempx += a[(n*4)];
                    }
                    return ((tempx)/32);
                }

                float tempy = 0;
                if (b = 'y'){while (n <= 32)
                    {
                        tempy += a[4(n+1)];
                    }
                    return ((tempy)/32);
                }

                float tempz = 0;
                if (b = 'z'){while (n <= 32)
                    {
                        tempz += a[4(n+2)];
                    }
                    return ((tempz)/32);
                }
            }
            while (true)

            {
                float x = accessor.ReadSingle(0); // first float
                float y = accessor.ReadSingle(4); // second float
                float z = accessor.ReadSingle(8); // third float
                int currentnode = accessor.ReadInt32(12);

                System.Threading.Thread.Sleep(16);
                int n = 0;
                while (n <= 32)
                {
                    CalCord[Calcheck - 3] = AveCalk(coords, 'x');
                    CalCord[Calcheck - 2] = AveCalk(coords, 'y');
                    CalCord[Calcheck - 1] = AveCalk(coords, 'z');
                    CalCord[Calcheck] = n;
                    
                }

                float VectorX = VChange(originX, x);
                float VectorY = VChange(originY, y);
                float VectorZ = VChange(originZ, z);
                Console.WriteLine($"C# read: {VectorX:F1}, {VectorY:F1}, {VectorZ:F1}, {currentnode:F1}");
            }
            
        }
        
    }
}