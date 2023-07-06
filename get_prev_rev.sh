# pr_number=$(echo "${{ github.event.pull_request.url }}" | awk -F'/' '{print $NF}')
pr_number='1'
GITHUB_TOKEN='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'
reviews=$(curl -s -X GET \
	-H "Accept: application/vnd.github.v3+json" \
	-H "Authorization: Bearer ${GITHUB_TOKEN}" \
	"https://api.github.com/repos/aalyth/work-test/pulls/${pr_number}/reviews")

reviewed='true' 
# TODO! check if the reviews are empty

tmp=$(echo "$reviews" | jq '.[0]')
echo $tmp

#if [ ${reviewed} == 'true' ]; then
#	last_review=$(echo "${reviews}" | jq -r 'map(select(.state == "APPROVED")) | last')
#	last_reviewer_grp=$(echo "${last_reviewer_grp}" | jq -r '.author_association')
#
#	echo "::set-output name=grp::${last_reviewer_grp}"
#
#else
#	echo "::set-output name=grp::''"
#fi
