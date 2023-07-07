pr_number='15'
GITHUB_TOKEN='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'
reviews=$(curl -s -X GET \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: Bearer ${GITHUB_TOKEN}" \
  "https://api.github.com/repos/aalyth/work-test/pulls/${pr_number}/reviews")

# approval_grps=''
approval_usrs=''

for review in $(echo "${reviews}" | jq -c '.[]' | tr -d ' ' ); do
	# if the current review is APPROVED
	if [ $(echo "${review}" | jq -r '.state') = 'APPROVED' ]; then
		# grp=$(echo "$review" | jq -r '.author_association')
		usr=$(echo "$review" | jq -r '.user.login')

		# if the review author's group is unique
		if ! $(echo "${approval_usrs}" | grep -q "${usr}") ; then
			# this check is so that the variable doesn't start with "\n"
			if [ "${approval_usrs}" = '' ]; then
				approval_usrs="${usr}"

			else
				approval_usrs="${approval_usrs}\n${usr}"
			fi
		fi
	fi
done

echo "${approval_usrs}"

required_approvals=2
if [ $(echo "${approval_usrs}" | wc -l) -lt "$required_approvals" ]; then
	exit 1
fi
