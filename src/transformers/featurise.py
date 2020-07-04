from sklearn.base import TransformerMixin, BaseEstimator


class FeaturiseCRF(BaseEstimator, TransformerMixin):
    def __init__(
        self, feature_order, shared_features, surrounding_features=None, bias=True
    ):
        self.feature_order = {feature: idx for idx, feature in enumerate(feature_order)}
        self.shared_features = shared_features
        self.surrounding_features = surrounding_features
        self.bias = bias

    def fit(self, *args, **kwargs):
        return self

    def featurise_entry(self, entry):
        def _featurise(entry, idx):
            token_features = dict()
            if self.bias:
                token_features["bias"] = True

            for shared_feature in self.shared_features:
                feature_idx = self.feature_order[shared_feature]
                token_features[f"word.{shared_feature}"] = entry[feature_idx][idx]

            if idx > 0:  # The word is not the first one...
                for feat in self.surrounding_features:
                    feature_idx = self.feature_order[feat]
                    token_features[f"-1:word.{feat}"] = entry[feature_idx][idx - 1]
            else:
                token_features["BOS"] = True

            if idx < len(entry[0]) - 1:  # The word is not the last one...
                for feat in self.surrounding_features:
                    feature_idx = self.feature_order[feat]
                    token_features[f"+1:word.{feat}"] = entry[feature_idx][idx + 1]
            else:
                token_features["EOS"] = True

            return token_features

        features = []
        for token_idx in range(len(entry[0])):
            features.append(_featurise(entry, token_idx))
        return features

    def transform(self, x, y=None):
        content = []
        for entry in x:
            content.append(self.featurise_entry(entry))
        return content
