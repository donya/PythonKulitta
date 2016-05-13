-- 2 - 5 pm


> import Euterpea
> t251 :: Music Pitch
> t251 = 
>  let dMinor = d 4 wn :=: f 4 wn :=: a 4 wn
>      gMajor =g 4 wn:=:b 4 wn:=:d 5 wn
>      cMajor =c 4 bn :=:e 4 bn :=:g 4 bn
>  in  dMinor :+: gMajor :+: cMajor

> prefixes :: [ a ] -> [ [ a ] ] 
> prefixes [ ] = [ ] 
> prefixes(x:xs)=let f pf =x:pf
>                in [x]: map f (prefixes xs)

> type Frequency = Double
> type Sample = Double
> type Seconds = Double

> sineTable :: Table
> sineTable = tableSinesN 4096 [1]

> mySound = AudSF Frequency Sample
> mySound = proc f -> do
>     s1 <- osc sineTable 0 -< f
>     s2 <- osc sineTable 0.2 -< f * 2
>     s3 <- osc sineTable 0.4 -< f * 4
>     returnA -< (s1 + 0.3 * s2 + 0.1 * s3) / 1.4

> myInstr :: Instr (Mono AudioRate)
> myInstr dur pch vol [amf, ama, fmf, fma] =
>     let d = fromRational dur
>         f = apToHzz pch
>         v = fromIntegral vol / 127.0
>     in proc _ -> do
>        f1 <- osc sineTable 0 -< fmf -- FM
>        let f2 = f + (f1 * fma * f)
>        a1 <- osc sineTable 0 -< amf -- AM
>        let amEnv = (1 - ama) + ama * (0.5 + a1/2)
>        s <- mySound -< f2
>        e <- envLineSeg [0, 1, 1, 0] (dFun d)
> myInstr dur pch vol params = myInstr dur pch vol [1, 0, 1, 0]

> dFun d = if d < 0.25 then [0.02 * d, 0.96 * d, 0.02 * d] else [0.05, d - 0.1, 0.05]

> myNote = proc _ -> do
>     mySound -< 440
> testMySound::
