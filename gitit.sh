git add .

echo "Please enter commit comment"

read commit

git commit -m $commit

git branch -M main

git push -u origin main
