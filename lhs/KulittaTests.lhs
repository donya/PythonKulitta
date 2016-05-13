Some Simple Kulitta Tests
Donya Quick
Last modified: 19-Feb-2016

> module KulittaTests where
> import Kulitta
> import Euterpea
> import System.Random

> testEq :: EqRel AbsPitch
> testEq a b = a `mod` 12 == b `mod` 12 -- tests if the pitch class is the same

> testSpace :: QSpace AbsPitch
> testSpace = [0..23] // testEq -- group two octaves of pitch numbers by pitch class
> testSpace2 = map (\x -> [x]) ([12..23]::[Int])

> testMel = [0,4,7,2] :: [AbsPitch] -- a simple melody: C,E,G,D

> testMelBuckets :: [EqClass AbsPitch]
> testMelBuckets = map (eqClass testSpace testEq) testMel -- find eq. classes ("buckets") for each melody note

===================================

Testing allSolns and versions of pairProg

> testAllSolns :: [[AbsPitch]]
> testAllSolns = allSolns testSpace testEq testMel

> testPred :: Predicate (AbsPitch, AbsPitch)
> testPred (a,b) = abs(a-b) <= 7

> testPairProg, testPairProg', testPairProg2 :: [[AbsPitch]]
> testPairProg = pairProg testSpace testEq testPred testMel
> testPairProg' = pairProg' testPred testMelBuckets
> testPairProg2 = pairProg testSpace testEq testPred testMel


--===================================

greedyProg and its variations are harder to test since they 
are stochastic, and random generation happens differently from 
one language to another.

> testFallback :: EqClass AbsPitch -> StdGen -> AbsPitch -> (StdGen, AbsPitch)
> testFallback bucket g x = if null bucket then error "empty!"
>                           else (g, head bucket)

> testGreedyProg :: Int -> [AbsPitch]
> testGreedyProg i = greedyProg testSpace testEq testPred testFallback (mkStdGen i) testMel

--> testGreedyProg' :: Int -> [AbsPitch]
--> testGreedyProg' i = greedyProg' testPred testFallback (mkStdGen i) testMelBuckets