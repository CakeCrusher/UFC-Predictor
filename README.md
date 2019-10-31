# UFC-Predictor
A compilation of machine learning models and neural networks (which are exclusively fed UFC data) designed to predict the outcome of an MMA fight by who won and the way by which they won.

This repository contrains scrapers for both https://www.sherdog.com/ and https://www.mixedmartialarts.com/ but it was primarily focused on https://www.sherdog.com/
This repository already contains a refined dataset of 4968 unique fights as well as an unrefined dataset with 10406 fights both scraped from https://www.sherdog.com/

The program predicts a possibility out of 4: Fighter A wins by Decision, Fighter A wins Inside The Distance, Fighter B wins by Decision, Fighter B wins Inside the Distance.
The coinflip exquivalent would be 25%

The machine learning models has so far achieved these results:
Format: M(Male)125(Weight) = UG(https://www.mixedmartialarts.com/ dataset)(48)(% chance of hitting)
M125 = UG(38)
M135 = UG(51)
M145 = UG(60)
M155 = UG(52)
M170 = SD(51)
M185 = SD(56)
M205 = SD(62)
M265 = SD(64)
Male = SD(53)
F115 = UG(69)
F125 = UG(65)
F135 = SD(59)
Female = SD(48)

The Recurrent Neural Network has achieved the following results:
Format: 145(weight)- 52,(% chance if it predicts 40(0 = extremely high certyainty of fighter A losing)<x<60(100 = extremely high certyainty of fighter A winning) 56,(% chance if it predicts 35<x<40 or 60<x<65) 58,(% chance if it predicts x<35 or 65<x) 47%,(% of total data(of specific dataset) that qualifies for 35<x<40 or 60<x<65) 14%(% of total data(of specific dataset) that qualifies for x<35 or 65<x)
115- 51, 50, 48, 69%, 40%

125- 55, 54, 58, 62%, 24%

135- 53, 51, 56, 62%, 29%

145- 52, 56, 58, 47%, 14%

155- 56, 60, 62, 61%, 30%

170- 58, 59, 62, 53%, 20%

185- 59, 61, 63, 68%, 40%

205- 55, 57, 63, 61%, 36%

265- 57, 56, 60, 69%, 40%

