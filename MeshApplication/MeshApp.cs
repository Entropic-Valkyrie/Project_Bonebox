using System;
using System.IO.MemoryMappedFiles;

class Program
{
    static void Main()
    {
        using (var mmf = MemoryMappedFile.OpenExisting("pose_basic"))
        using (var accessor = mmf.CreateViewAccessor())
        {
            int Calcheck = 0;
            float XSum = 0;
            float YSum = 0;
            float ZSum = 0;
            static float VChange (float a, float b)
            {
                    return Math.Abs((a + b));
            }
            while (true)
            {
                float x = accessor.ReadSingle(0); // first float
                float y = accessor.ReadSingle(4); // second float
                float z = accessor.ReadSingle(8); // third float
                if (Calcheck != 10) {Calcheck += 1; XSum += x; YSum += y; ZSum += z;}
                //Console.WriteLine($"C# read: {x:F1}, {y:F1}, {z:F1}");
                float originX = (XSum/10);
                float originY = (YSum/10);
                float originZ = (ZSum/10);
                System.Threading.Thread.Sleep(16);

                float VectorX = VChange(originX, x);
                float VectorY = VChange(originY, y);
                float VectorZ = VChange(originZ, z);
                Console.WriteLine($"C# read: {VectorX:F1}, {VectorY:F1}, {VectorZ:F1}");
            }
            
        }
        
    }
}