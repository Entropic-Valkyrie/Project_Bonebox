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
            }
            while (true)

            {
                float x = accessor.ReadSingle(0); // first float
                float y = accessor.ReadSingle(4); // second float
                float z = accessor.ReadSingle(8); // third float
                int currentnode = accessor.ReadInt32(12);

                System.Threading.Thread.Sleep(16);
                
            }
            
        }
        
    }
}